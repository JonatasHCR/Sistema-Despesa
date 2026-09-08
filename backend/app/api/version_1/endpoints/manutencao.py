from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.version_1.dependencies import get_current_admin
from app.core.database import get_db
from app.model.user import User
from app.service.manutencao import (
    ALVOS,
    ErroDeManutencao,
    Filtros,
    ManutencaoService,
)


class BackupSchema(BaseModel):
    nome: str
    bytes: int
    criado_em: datetime


class AlvoSchema(BaseModel):
    chave: str
    rotulo: str
    aceita_filtros: bool


class FiltrosSchema(BaseModel):
    """Restringe a limpeza. Todos opcionais, combinados com AND.

    O antigo `mes` virou o par `de`/`ate`: um mês fechado não cobre "de 15/03 a
    15/04", que é como as pessoas de fato agrupam vencimentos.
    """

    de: str | None = Field(None, description="AAAA-MM-DD — vencimento a partir de (inclusive)")
    ate: str | None = Field(None, description="AAAA-MM-DD — vencimento até (inclusive)")
    status: str | None = Field(None, description="P = pendente (não paga), Q = quitada (paga)")
    tipo: str | None = Field(None, description="Tipo exato (ver GET /manutencao/tipos)")
    nome: str | None = Field(None, description="Trecho do nome da despesa")
    usuario_id: int | None = Field(None, description="Só as despesas deste usuário")

    def para_servico(self) -> Filtros:
        return Filtros(
            de=self.de,
            ate=self.ate,
            status=self.status,
            tipo=self.tipo,
            nome=self.nome,
            usuario_id=self.usuario_id,
        )


class ContagemSchema(BaseModel):
    alvo: str
    filtros: FiltrosSchema = Field(default_factory=FiltrosSchema)


class ContagemResultado(BaseModel):
    total: int


class LimpezaSchema(BaseModel):
    alvo: str = Field(..., description="Chave do alvo (ver GET /manutencao/alvos)")
    filtros: FiltrosSchema = Field(default_factory=FiltrosSchema)
    confirmacao: str = Field(
        ...,
        description="Precisa ser exatamente LIMPAR — a operação é irreversível",
    )


class RestauracaoSchema(BaseModel):
    nome: str
    confirmacao: str = Field(
        ...,
        description="Precisa ser exatamente RESTAURAR — substitui os dados atuais",
    )


class ResultadoSchema(BaseModel):
    mensagem: str
    detalhes: dict[str, int] | None = None


class ManutencaoEndpoint:
    """Administração do banco: backup, restauração e limpeza.

    Todas as rotas exigem `get_current_admin` — o papel local `tb_users.admin`,
    que vem de dois lugares e só deles: o script `promover_admin.py`, e a conta
    mestra declarada em ADMIN_MESTRE_EMAIL no .env do servidor. A tela não
    promove ninguém, de propósito: senão qualquer pessoa com acesso a ela se
    promoveria.

    As duas operações destrutivas pedem uma palavra digitada. É proteção contra
    o clique errado, não contra intenção: quem pode chamar a rota já passou pelo
    papel de admin. Contra intenção, o que vale é o backup.
    """

    def __init__(self):
        self.router = APIRouter(prefix="/manutencao", tags=["Manutencao"])
        self.register_routes()

    def register_routes(self):
        self.router.get("/backups", response_model=list[BackupSchema])(self.listar)
        self.router.post(
            "/backups", response_model=BackupSchema, status_code=status.HTTP_201_CREATED
        )(self.gerar)
        self.router.get("/backups/{nome}")(self.baixar)
        self.router.get("/alvos", response_model=list[AlvoSchema])(self.alvos)
        self.router.get("/tipos", response_model=list[str])(self.tipos)
        self.router.post("/contagem", response_model=ContagemResultado)(self.contar)
        self.router.post("/limpeza", response_model=ResultadoSchema)(self.limpar)
        self.router.post("/restauracao", response_model=ResultadoSchema)(self.restaurar)

    async def listar(
        self,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_admin),
    ):
        return ManutencaoService(db).listar()

    async def gerar(
        self,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_admin),
    ):
        try:
            return await ManutencaoService(db).gerar_backup()
        except ErroDeManutencao as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    async def baixar(
        self,
        nome: str,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_admin),
    ):
        try:
            caminho = ManutencaoService(db).resolver_arquivo(nome)
        except ErroDeManutencao as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
        return FileResponse(
            caminho, media_type="application/octet-stream", filename=caminho.name
        )

    async def alvos(self, _: User = Depends(get_current_admin)):
        return [
            {"chave": chave, "rotulo": cfg["rotulo"], "aceita_filtros": cfg["aceita_filtros"]}
            for chave, cfg in ALVOS.items()
        ]

    async def tipos(
        self,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_admin),
    ):
        """Os tipos que existem hoje, para o seletor da tela.

        `tb_despesas.tipo` e texto livre, sem tabela de dominio — a lista so
        pode sair dos proprios dados.
        """
        return await ManutencaoService(db).tipos_existentes()

    async def contar(
        self,
        dados: ContagemSchema,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_admin),
    ):
        """Quantas despesas o filtro alcanca — sem apagar nada.

        Nao pede confirmacao porque nao muda nada. Existe para a limpeza
        filtrada deixar de ser um tiro no escuro: com periodo, status, tipo e
        nome combinados, a unica outra forma de saber o que o filtro pega seria
        apagando, e a volta seria restaurar o banco inteiro.
        """
        try:
            total = await ManutencaoService(db).contar(
                dados.alvo, filtros=dados.filtros.para_servico()
            )
        except ErroDeManutencao as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
        return {"total": total}

    async def limpar(
        self,
        dados: LimpezaSchema,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_admin),
    ):
        if dados.confirmacao != "LIMPAR":
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Digite LIMPAR para confirmar. Nada foi apagado.",
            )
        try:
            removidos = await ManutencaoService(db).limpar(
                dados.alvo, filtros=dados.filtros.para_servico()
            )
        except ErroDeManutencao as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

        total = sum(removidos.values())
        return {
            "mensagem": f"{total} registro(s) removido(s) por {admin.email}.",
            "detalhes": removidos,
        }

    async def restaurar(
        self,
        dados: RestauracaoSchema,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_admin),
    ):
        if dados.confirmacao != "RESTAURAR":
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Digite RESTAURAR para confirmar. Nada foi alterado.",
            )
        try:
            arquivo = await ManutencaoService(db).restaurar(dados.nome)
        except ErroDeManutencao as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

        return {
            "mensagem": f"Banco restaurado a partir de {arquivo} por {admin.email}. "
            "Recarregue a página.",
            "detalhes": None,
        }
