"""Autenticação via Keycloak: validação do token, gate de grupo e provisionamento.

São os testes que sustentam a troca do JWT próprio pelo SSO. Cada um cobre uma
maneira de o desenho falhar em silêncio.
"""

import pytest
from sqlalchemy import func, select

from app.model.user import User
from tests.support import oidc


URL = "/users/"
SUB = "aaaaaaaa-0000-0000-0000-000000000001"


async def _quantos_usuarios(db) -> int:
    return (await db.execute(select(func.count()).select_from(User))).scalar_one()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_sem_o_grupo_recebe_403_e_nao_e_provisionado(async_client, async_db):
    """A checagem que impede o provisionamento de abrir o sistema ao realm todo.

    Sem ela, qualquer pessoa autenticada no Keycloak — inclusive quem só usa a
    receita — entraria na despesa e ainda ganharia uma linha em tb_users. O
    portal esconde o cartão, mas quem digitar a URL chega aqui.
    """
    antes = await _quantos_usuarios(async_db)

    token = oidc.cunhar_token(
        SUB, "so.receita@ufc.com.br", groups=["/apps/receita"]
    )
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 403
    assert await _quantos_usuarios(async_db) == antes


@pytest.mark.asyncio
@pytest.mark.integration
async def test_sem_nenhum_grupo_recebe_403(async_client):
    token = oidc.cunhar_token(SUB, "ninguem@ufc.com.br", groups=[])
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 403


@pytest.mark.asyncio
@pytest.mark.integration
async def test_emissor_diferente_e_recusado(async_client):
    """Token assinado pela chave certa, mas emitido por outro realm."""
    token = oidc.cunhar_token(
        SUB, "alguem@ufc.com.br", issuer="http://outro-keycloak/realms/qualquer"
    )
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_audiencia_diferente_e_recusada(async_client):
    """Um token válido do inventário não vale para a despesa."""
    token = oidc.cunhar_token(SUB, "alguem@ufc.com.br", audience="inventario-api")
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_expirado_e_recusado(async_client):
    token = oidc.cunhar_token(SUB, "alguem@ufc.com.br", expirado=True)
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_sem_assinatura_valida_e_recusado(async_client):
    resposta = await async_client.get(
        URL, headers={"Authorization": "Bearer nao.e.um.token"}
    )
    assert resposta.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_primeiro_acesso_provisiona_com_external_id(async_client, async_db):
    email = "novo@ufc.com.br"
    token = oidc.cunhar_token(SUB, email, nome="Fulano da Silva")

    resposta = await async_client.get(
        f"{URL}email/{email}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resposta.status_code == 200

    criado = (
        await async_db.execute(select(User).where(User.email == email))
    ).scalar_one()
    assert criado.external_id == SUB
    assert criado.nome == "Fulano da Silva"
    assert criado.senha is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_conta_anterior_ao_sso_e_reaproveitada_pelo_email(async_client, async_db):
    """O ponto que preserva as FKs.

    Quem já tinha conta precisa continuar com o MESMO id — há despesas,
    destinatários e configurações de notificação apontando para ele. O casamento
    por email acontece uma vez; daí em diante é pelo external_id.
    """
    antigo = User(nome="ja existia", email="antigo@ufc.com.br", senha="$argon2$hash")
    async_db.add(antigo)
    await async_db.commit()
    await async_db.refresh(antigo)
    id_original = antigo.id

    token = oidc.cunhar_token(SUB, "antigo@ufc.com.br")
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200

    # Reconsulta em vez de refresh: o commit da aplicação destacou a instância
    # que este teste segurava.
    depois = (
        await async_db.execute(select(User).where(User.email == "antigo@ufc.com.br"))
    ).scalar_one()
    assert depois.id == id_original
    assert depois.external_id == SUB
    assert await _quantos_usuarios(async_db) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_email_com_caixa_diferente_nao_duplica_conta(async_client, async_db):
    """O Keycloak não garante a caixa do email; o banco tem UNIQUE em email."""
    antigo = User(nome="ja existia", email="pessoa@ufc.com.br")
    async_db.add(antigo)
    await async_db.commit()

    token = oidc.cunhar_token(SUB, "Pessoa@UFC.com.br")
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert await _quantos_usuarios(async_db) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_nome_repetido_nao_quebra_o_provisionamento(async_client, async_db):
    """`tb_users.nome` é UNIQUE, herança de quando o nome era o login.

    Dois homônimos no Keycloak violariam a constraint no segundo provisionamento.
    """
    async_db.add(User(nome="Maria Silva", email="maria1@ufc.com.br"))
    await async_db.commit()

    token = oidc.cunhar_token(SUB, "maria2@ufc.com.br", nome="Maria Silva")
    resposta = await async_client.get(URL, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200

    nova = (
        await async_db.execute(select(User).where(User.email == "maria2@ufc.com.br"))
    ).scalar_one()
    assert nova.nome == "maria2@ufc.com.br"  # cai para o email como desempate
    assert await _quantos_usuarios(async_db) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_perder_o_grupo_barra_sem_apagar_a_conta(async_client, async_db):
    """Tirar do grupo barra o acesso, e a conta continua existindo.

    Há despesas, destinatários e configurações de notificação apontando para a
    linha; apagá-la levaria histórico junto.

    A virada de `ativo` para False não é observável daqui: o `get_db` faz
    rollback quando uma exceção sobe, e no conftest a sessão é compartilhada e
    presa a uma transação externa, então o rollback desfaz até o que já havia
    sido commitado. Em produção cada requisição tem sessão própria e o commit
    persiste. O caminho de volta (`ativo` = True) é testado logo abaixo, e esse
    não passa por exceção.
    """
    email = "saiu@ufc.com.br"
    await async_client.get(
        URL, headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email)}"}
    )
    criado = (
        await async_db.execute(select(User).where(User.email == email))
    ).scalar_one()
    assert criado.ativo is True
    # Guarda o valor, nao a instancia: o rollback do 403 a destaca da sessao.
    id_original = criado.id

    # Mesma pessoa, agora sem o grupo.
    resposta = await async_client.get(
        URL,
        headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email, groups=[])}"},
    )
    assert resposta.status_code == 403

    # De volta ao grupo: tem que ser a MESMA linha, não uma recriada.
    resposta = await async_client.get(
        URL, headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email)}"}
    )
    assert resposta.status_code == 200

    depois = (
        await async_db.execute(select(User).where(User.email == email))
    ).scalar_one()
    assert depois.id == id_original, "a conta não pode ser recriada"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_devolver_o_grupo_reativa_a_conta(async_client, async_db):
    email = "voltou@ufc.com.br"
    await async_client.get(
        URL, headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email)}"}
    )
    await async_client.get(
        URL,
        headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email, groups=[])}"},
    )

    resposta = await async_client.get(
        URL, headers={"Authorization": f"Bearer {oidc.cunhar_token(SUB, email)}"}
    )
    assert resposta.status_code == 200

    user = (
        await async_db.execute(select(User).where(User.email == email))
    ).scalar_one()
    assert user.ativo is True
