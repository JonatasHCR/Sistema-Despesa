"""Backup, restauração e limpeza do banco — a tela de Administração.

`pg_dump`/`pg_restore` rodam neste container. Mandar num sidecar exigiria o
socket do Docker, o que daria a qualquer falha no app o poder de criar
containers na máquina.

Os arquivos caem no diretório do sidecar de backup, então os agendados e os do
botão ficam na mesma lista.
"""

from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DespesaStatusEnum
from app.core.settings import Settings

DIRETORIO_BACKUPS = Path(os.environ.get("BACKUP_DIR", "/backups"))

# Só nomes gerados por nós. Fecha a porta para `../../etc/passwd` chegar ao
# download ou à restauração por um parâmetro de rota.
NOME_VALIDO = re.compile(r"^[A-Za-z0-9._-]+\.(dump|sql\.gz|sql)$")


# O `pg_restore` sai com código 1 se ignorou QUALQUER erro, inclusive o
# inofensivo `SET transaction_timeout` que um cliente mais novo que o servidor
# escreve. Aceitar o código em bloco daria por boa uma restauração que perdeu
# tabelas; tolerar pelo nome, não.
TOLERADOS_NO_RESTORE = ('unrecognized configuration parameter "transaction_timeout"',)


class ErroDeManutencao(RuntimeError):
    """Falha esperada, para virar 4xx/5xx com mensagem útil."""


@dataclass(frozen=True)
class Backup:
    nome: str
    bytes: int
    criado_em: datetime


@dataclass(frozen=True)
class Filtros:
    """Restringe uma limpeza. Opcionais, combinados com AND; nenhum
    preenchido apaga o alvo inteiro.
    """

    de: str | None = None          # AAAA-MM-DD, vencimento >= (inclusive)
    ate: str | None = None         # AAAA-MM-DD, vencimento <= (inclusive)
    status: str | None = None      # 'P' pendente | 'Q' quitada
    tipo: str | None = None        # igualdade, sem diferenciar maiúsculas
    nome: str | None = None        # trecho do nome
    usuario_id: int | None = None


# Cada alvo apaga em ordem de dependência (filhos antes dos pais). `tb_users`
# não é alvo: levaria junto o histórico de quem lançou cada despesa.
ALVOS: dict[str, dict] = {
    "despesas": {
        "rotulo": "Despesas (e destinatários)",
        "tabelas": ["tb_despesa_destinatarios", "tb_despesas"],
        "aceita_filtros": True,
    },
    "notificacoes": {
        "rotulo": "Configurações de notificação",
        "tabelas": ["tb_notificacao_config"],
        "aceita_filtros": False,
    },
    "tudo": {
        "rotulo": "Tudo (dados de negócio — NÃO inclui usuários)",
        "tabelas": [
            "tb_despesa_destinatarios",
            "tb_despesas",
            "tb_notificacao_config",
        ],
        "aceita_filtros": False,
    },
}


class ManutencaoService:
    def __init__(self, session: AsyncSession, settings: Settings | None = None):
        self.session = session
        self.settings = settings or Settings()

    # -- utilidades ---------------------------------------------------------

    def _ambiente_pg(self) -> dict[str, str]:
        return {**os.environ, "PGPASSWORD": self.settings.DB_PASSWORD}

    def _conexao(self) -> list[str]:
        return [
            "-h", self.settings.DB_HOST,
            "-p", str(self.settings.DB_PORT),
            "-U", self.settings.DB_USER,
            "-d", self.settings.DB_NAME,
        ]

    async def _rodar(self, *args: str, tolerar: tuple[str, ...] = ()) -> str:
        """Roda um utilitário do Postgres. Devolve o stderr; levanta se falhou.

        O código de saída sozinho não serve de veredito — ver
        TOLERADOS_NO_RESTORE.
        """
        processo = await asyncio.create_subprocess_exec(
            *args,
            env=self._ambiente_pg(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, saida = await processo.communicate()
        erro = saida.decode(errors="replace").strip()
        if processo.returncode == 0:
            return erro

        linhas = [linha for linha in erro.splitlines() if ": error: " in linha]
        graves = [
            linha for linha in linhas
            if not any(trecho in linha for trecho in tolerar)
        ]
        # Sem nenhuma linha de erro reconhecível a falha é desconhecida, e dá-la
        # por boa seria pior do que reclamar sem saber o motivo.
        if graves or not linhas:
            detalhe = (graves or erro.splitlines() or ["sem detalhe"])[-1]
            raise ErroDeManutencao(f"{args[0]} falhou: {detalhe}")

        return erro

    def resolver_arquivo(self, nome: str) -> Path:
        """Traduz um nome de backup em caminho, recusando qualquer travessia."""
        if not NOME_VALIDO.match(nome):
            raise ErroDeManutencao("Nome de arquivo inválido.")

        caminho = (DIRETORIO_BACKUPS / nome).resolve()
        if caminho.parent != DIRETORIO_BACKUPS.resolve() or not caminho.is_file():
            raise ErroDeManutencao("Backup não encontrado.")
        return caminho

    # -- operações ----------------------------------------------------------

    def listar(self) -> list[Backup]:
        if not DIRETORIO_BACKUPS.is_dir():
            return []

        achados = [
            Backup(
                nome=f.name,
                bytes=f.stat().st_size,
                criado_em=datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc),
            )
            for f in DIRETORIO_BACKUPS.iterdir()
            if f.is_file() and NOME_VALIDO.match(f.name)
        ]
        return sorted(achados, key=lambda b: b.criado_em, reverse=True)

    async def gerar_backup(self) -> Backup:
        DIRETORIO_BACKUPS.mkdir(parents=True, exist_ok=True)
        nome = f"despesa-{datetime.now().strftime('%Y%m%d-%H%M%S')}.dump"
        destino = DIRETORIO_BACKUPS / nome

        await self._rodar("pg_dump", "-Fc", *self._conexao(), "-f", str(destino))

        if not destino.is_file() or destino.stat().st_size == 0:
            raise ErroDeManutencao("O pg_dump terminou mas não gerou arquivo.")

        return Backup(
            nome=nome,
            bytes=destino.stat().st_size,
            criado_em=datetime.now(timezone.utc),
        )

    async def restaurar(self, nome: str) -> str:
        """Substitui os dados atuais pelos do arquivo. Irreversível."""
        arquivo = self.resolver_arquivo(nome)

        # A sessão precisa sair do caminho: o pg_restore vai derrubar as tabelas
        # que ela mantém abertas, e uma conexão presa vira deadlock.
        await self.session.close()

        await self._rodar(
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            *self._conexao(),
            str(arquivo),
            tolerar=TOLERADOS_NO_RESTORE,
        )
        return arquivo.name

    def _monta_filtro(self, config: dict, f: Filtros) -> tuple[str, dict]:
        """Traduz os filtros numa cláusula WHERE sobre `tb_despesas`.

        Tudo por parâmetro vinculado: são valores digitados chegando a um DELETE.
        """
        if not config["aceita_filtros"]:
            return "", {}

        condicoes: list[str] = []
        parametros: dict = {}

        # Pontas inclusivas: é como se lê "de 01/03 a 31/03". O valor vai como
        # `date` porque o asyncpg deduz o tipo pela coluna e recusa string. A
        # regex garante a forma; o `fromisoformat`, que a data existe.
        limites: dict[str, date] = {}
        for nome, valor, operador in (
            ("de", f.de, ">="),
            ("ate", f.ate, "<="),
        ):
            if not valor:
                continue
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
                raise ErroDeManutencao(
                    f"Data {nome!r} deve estar no formato AAAA-MM-DD."
                )
            try:
                limites[nome] = date.fromisoformat(valor)
            except ValueError:
                raise ErroDeManutencao(f"Data {nome!r} não existe no calendário.")
            condicoes.append(f"vencimento {operador} :{nome}")
            parametros[nome] = limites[nome]

        if "de" in limites and "ate" in limites and limites["de"] > limites["ate"]:
            raise ErroDeManutencao("A data inicial é posterior à final.")

        if f.status:
            validos = {s.value for s in DespesaStatusEnum}
            if f.status not in validos:
                raise ErroDeManutencao(
                    f"Status inválido: {f.status!r}. Use um de {sorted(validos)}."
                )
            condicoes.append("status = :status")
            parametros["status"] = f.status

        if f.tipo:
            # Igualdade, não LIKE: um LIKE faria "CONTAS" alcançar
            # "CONTAS DE CONSUMO".
            condicoes.append("UPPER(tipo) = UPPER(:tipo)")
            parametros["tipo"] = f.tipo.strip()

        if f.nome:
            # Parcial, com os curingas escapados: um "%" digitado procura "%",
            # não "qualquer coisa".
            termo = f.nome.strip().replace("\\", "\\\\")
            termo = termo.replace("%", "\\%").replace("_", "\\_")
            # `UPPER(...) LIKE UPPER(...)` e nao `ILIKE`: o ILIKE so existe no
            # Postgres, e a suite de testes roda em SQLite — com ele, o unico
            # jeito de exercitar este filtro seria em producao.
            condicoes.append("UPPER(nome) LIKE UPPER(:nome) ESCAPE '\\'")
            parametros["nome"] = f"%{termo}%"

        if f.usuario_id:
            condicoes.append("user_id = :usuario_id")
            parametros["usuario_id"] = f.usuario_id

        filtro = " WHERE " + " AND ".join(condicoes) if condicoes else ""
        return filtro, parametros

    async def contar(self, alvo: str, filtros: Filtros | None = None) -> int:
        """Quantas despesas o filtro alcança, sem apagar nada.

        A limpeza é irreversível e a combinação de filtros não é óbvia de ler:
        sem esta contagem, descobrir o alcance exigiria apagar.
        """
        config = ALVOS.get(alvo)
        if config is None:
            raise ErroDeManutencao(f"Alvo de limpeza inválido: {alvo!r}.")

        filtro, parametros = self._monta_filtro(config, filtros or Filtros())
        if "tb_despesas" not in config["tabelas"]:
            return 0

        resultado = await self.session.execute(
            text(f"SELECT count(*) FROM tb_despesas{filtro}"), parametros
        )
        return int(resultado.scalar() or 0)

    async def tipos_existentes(self) -> list[str]:
        """`tb_despesas.tipo` é texto livre, sem tabela de domínio: a lista do
        seletor só pode sair dos próprios dados.
        """
        resultado = await self.session.execute(
            text("SELECT DISTINCT tipo FROM tb_despesas ORDER BY tipo")
        )
        return [linha[0] for linha in resultado.all() if linha[0]]

    async def limpar(
        self,
        alvo: str,
        filtros: Filtros | None = None,
    ) -> dict[str, int]:
        """Apaga dados de negócio. Devolve quantas linhas saíram de cada tabela."""
        config = ALVOS.get(alvo)
        if config is None:
            raise ErroDeManutencao(f"Alvo de limpeza inválido: {alvo!r}.")

        filtro, parametros = self._monta_filtro(config, filtros or Filtros())

        removidos: dict[str, int] = {}
        for tabela in config["tabelas"]:
            if filtro and tabela == "tb_despesa_destinatarios":
                # Sem colunas próprias para filtrar: saem junto com as
                # despesas que o filtro alcança.
                comando = text(
                    "DELETE FROM tb_despesa_destinatarios WHERE despesa_id IN "
                    f"(SELECT id FROM tb_despesas{filtro})"
                )
            elif filtro and tabela == "tb_despesas":
                comando = text(f"DELETE FROM tb_despesas{filtro}")
            else:
                comando = text(f"DELETE FROM {tabela}")

            resultado = await self.session.execute(comando, parametros)
            removidos[tabela] = resultado.rowcount or 0

        await self.session.commit()
        return removidos
