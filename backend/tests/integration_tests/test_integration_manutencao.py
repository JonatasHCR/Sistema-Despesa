"""Tela de Administração: backup, limpeza e restauração.

O que estes testes protegem: uma tela que apaga banco não pode depender só de
estar escondida no menu.
"""

import pytest
from sqlalchemy import select

from app.model.user import User
from tests.support import oidc


URL = "/manutencao"
SUB_ADMIN = "bbbbbbbb-0000-0000-0000-000000000001"
SUB_COMUM = "cccccccc-0000-0000-0000-000000000002"


async def _entrar(async_client, async_db, sub, email, admin):
    """Provisiona pelo primeiro acesso e devolve os cabeçalhos."""
    headers = {"Authorization": f"Bearer {oidc.cunhar_token(sub, email)}"}
    await async_client.get(f"/users/email/{email}", headers=headers)

    user = (
        await async_db.execute(select(User).where(User.email == email))
    ).scalar_one()
    if user.admin != admin:
        user.admin = admin
        await async_db.commit()
    return headers


@pytest.mark.asyncio
@pytest.mark.integration
async def test_usuario_comum_nao_entra_em_nenhuma_rota(async_client, async_db):
    """O papel é a defesa; esconder o link no menu não é."""
    headers = await _entrar(
        async_client, async_db, SUB_COMUM, "comum@ufc.com.br", admin=False
    )

    for metodo, caminho, corpo in [
        ("get", f"{URL}/backups", None),
        ("post", f"{URL}/backups", {}),
        ("get", f"{URL}/alvos", None),
        ("post", f"{URL}/limpeza", {"alvo": "tudo", "confirmacao": "LIMPAR"}),
        ("post", f"{URL}/restauracao", {"nome": "x.dump", "confirmacao": "RESTAURAR"}),
    ]:
        chamada = getattr(async_client, metodo)
        resposta = (
            await chamada(caminho, headers=headers)
            if corpo is None
            else await chamada(caminho, json=corpo, headers=headers)
        )
        assert resposta.status_code == 403, f"{metodo.upper()} {caminho} deixou passar"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_sem_token_tambem_nao_entra(async_client):
    assert (await async_client.get(f"{URL}/backups")).status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_ve_os_alvos_de_limpeza(async_client, async_db):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    resposta = await async_client.get(f"{URL}/alvos", headers=headers)

    assert resposta.status_code == 200
    chaves = {a["chave"] for a in resposta.json()}
    assert chaves == {"despesas", "notificacoes", "tudo"}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_limpeza_sem_a_palavra_certa_nao_apaga(async_client, async_db):
    """A confirmação digitada protege do clique errado, não da intenção."""
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    resposta = await async_client.post(
        f"{URL}/limpeza",
        json={"alvo": "tudo", "confirmacao": "limpar"},  # minúsculo
        headers=headers,
    )
    assert resposta.status_code == 400
    assert "LIMPAR" in resposta.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_alvo_invalido_e_recusado(async_client, async_db):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    resposta = await async_client.post(
        f"{URL}/limpeza",
        json={"alvo": "tb_users", "confirmacao": "LIMPAR"},
        headers=headers,
    )
    assert resposta.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_download_recusa_travessia_de_caminho(async_client, async_db):
    """`../` num parâmetro de rota não pode virar leitura de arquivo do host."""
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    for nome in ["../../etc/passwd", "..%2F..%2Fetc%2Fpasswd", "qualquer.txt"]:
        resposta = await async_client.get(f"{URL}/backups/{nome}", headers=headers)
        assert resposta.status_code in (404, 400), f"{nome} não foi barrado"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_restauracao_sem_a_palavra_certa_nao_toca_no_banco(
    async_client, async_db
):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    resposta = await async_client.post(
        f"{URL}/restauracao",
        json={"nome": "qualquer.dump", "confirmacao": "sim"},
        headers=headers,
    )
    assert resposta.status_code == 400
    assert "RESTAURAR" in resposta.json()["detail"]


# ---------------------------------------------------------------------------
# Filtros da limpeza
# ---------------------------------------------------------------------------
#
# Estes montam a clausula WHERE de um DELETE irreversivel. Um filtro que
# alcanca mais do que deveria nao da erro nenhum — so apaga demais, e a unica
# volta seria restaurar o banco inteiro. Por isso cada um e conferido pelo que
# SOBROU, nao so pelo que saiu.


async def _semear(async_db, user_id):
    """Quatro despesas que se distinguem em todos os eixos filtraveis."""
    from datetime import date

    from app.model.despesa import Despesa

    linhas = [
        # nome,                tipo,     status, vencimento
        ("Anuidade CREA",      "CREA",   "Q", date(2025, 3, 10)),
        ("Boleto da grafica",  "BOLETO", "P", date(2025, 3, 20)),
        ("Boleto do papel",    "BOLETO", "Q", date(2026, 1, 15)),
        ("Aluguel 100% sala",  "ALUGUEL", "P", date(2026, 7, 1)),
    ]
    for nome, tipo, status, vencimento in linhas:
        async_db.add(Despesa(
            nome=nome, tipo=tipo, valor=100, status=status,
            vencimento=vencimento, user_id=user_id,
        ))
    await async_db.commit()


async def _contar(async_client, headers, filtros):
    resposta = await async_client.post(
        f"{URL}/contagem",
        json={"alvo": "despesas", "filtros": filtros},
        headers=headers,
    )
    return resposta.status_code, resposta.json()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contagem_nao_apaga_e_separa_pagas_de_nao_pagas(async_client, async_db):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    user = (
        await async_db.execute(select(User).where(User.email == "chefe@ufc.com.br"))
    ).scalar_one()
    await _semear(async_db, user.id)

    _, tudo = await _contar(async_client, headers, {})
    _, pagas = await _contar(async_client, headers, {"status": "Q"})
    _, nao_pagas = await _contar(async_client, headers, {"status": "P"})

    assert tudo["total"] == 4
    assert pagas["total"] == 2
    assert nao_pagas["total"] == 2
    # A contagem e so leitura: nada pode ter sumido no caminho.
    _, depois = await _contar(async_client, headers, {})
    assert depois["total"] == 4


@pytest.mark.asyncio
@pytest.mark.integration
async def test_periodo_de_vencimento_inclui_as_duas_pontas(async_client, async_db):
    """"de 10/03 a 20/03" tem que pegar o dia 10 e o dia 20."""
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    user = (
        await async_db.execute(select(User).where(User.email == "chefe@ufc.com.br"))
    ).scalar_one()
    await _semear(async_db, user.id)

    _, r = await _contar(
        async_client, headers, {"de": "2025-03-10", "ate": "2025-03-20"}
    )
    assert r["total"] == 2, "as pontas do periodo deveriam entrar"

    _, r = await _contar(async_client, headers, {"de": "2026-01-01"})
    assert r["total"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_curinga_no_nome_e_procurado_como_texto(async_client, async_db):
    """Um "%" digitado procura "%", nao "qualquer coisa"."""
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    user = (
        await async_db.execute(select(User).where(User.email == "chefe@ufc.com.br"))
    ).scalar_one()
    await _semear(async_db, user.id)

    _, r = await _contar(async_client, headers, {"nome": "%"})
    assert r["total"] == 1, "o % deveria casar so com 'Aluguel 100% sala'"


# Um caso por execucao, e nao um laco: a fixture prende a sessao numa transacao
# externa, e o rollback disparado pelo 400 a desfaz — junto com o `admin=True`
# e com as despesas semeadas. Da segunda volta em diante o teste mediria um 403
# em vez do filtro. Com `parametrize` cada caso ganha banco e sessao novos.
#
# Pelo mesmo motivo aqui NAO se afirma "nada foi apagado": depois do rollback
# nao ha estado observavel para comparar. Que a rejeicao acontece antes de
# qualquer DELETE e estrutural — `_monta_filtro` levanta enquanto monta o WHERE,
# antes do laco que executa —, e a contrapartida positiva (so as linhas do
# filtro saem) esta em `test_limpeza_filtrada_apaga_so_o_que_o_filtro_alcanca`.
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("filtros", [
    {"status": "X"},                            # status fora do dominio
    {"de": "01/2025"},                          # formato errado
    {"de": "2025-02-30"},                       # data que nao existe
    {"de": "2026-01-01", "ate": "2025-01-01"},  # inicio depois do fim
])
async def test_filtro_invalido_recusado_antes_de_apagar(
    async_client, async_db, filtros
):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    user = (
        await async_db.execute(select(User).where(User.email == "chefe@ufc.com.br"))
    ).scalar_one()
    await _semear(async_db, user.id)

    resposta = await async_client.post(
        f"{URL}/limpeza",
        json={"alvo": "despesas", "filtros": filtros, "confirmacao": "LIMPAR"},
        headers=headers,
    )
    assert resposta.status_code == 400, f"{filtros} passou"
    assert "LIMPAR" not in resposta.json()["detail"], (
        "a recusa veio da confirmacao, nao do filtro — o filtro nem foi avaliado"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_limpeza_filtrada_apaga_so_o_que_o_filtro_alcanca(async_client, async_db):
    headers = await _entrar(
        async_client, async_db, SUB_ADMIN, "chefe@ufc.com.br", admin=True
    )
    user = (
        await async_db.execute(select(User).where(User.email == "chefe@ufc.com.br"))
    ).scalar_one()
    await _semear(async_db, user.id)

    filtros = {"status": "Q", "tipo": "BOLETO"}
    _, previa = await _contar(async_client, headers, filtros)
    assert previa["total"] == 1

    resposta = await async_client.post(
        f"{URL}/limpeza",
        json={"alvo": "despesas", "filtros": filtros, "confirmacao": "LIMPAR"},
        headers=headers,
    )
    assert resposta.status_code == 200
    # O que a previa prometeu e o que saiu tem que ser o mesmo numero: e nisso
    # que o admin se apoia para apertar o botao.
    assert resposta.json()["detalhes"]["tb_despesas"] == previa["total"]

    _, sobrou = await _contar(async_client, headers, {})
    assert sobrou["total"] == 3
    # O outro BOLETO, o pendente, tinha de sobreviver.
    _, boletos = await _contar(async_client, headers, {"tipo": "BOLETO"})
    assert boletos["total"] == 1
