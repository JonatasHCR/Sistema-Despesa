import pytest


URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_update_get_delete_user(async_client, auth):
    # A conta já existe: foi provisionada na primeira chamada autenticada, que
    # é como toda conta nasce agora. Não há mais POST /users/ público.
    user_id = auth["user"]["id"]
    headers = auth["headers"]

    response_update = await async_client.put(
        f"{URL_USER}{user_id}",
        json={"nome": "User Teste Alterado"},
        headers=headers,
    )
    assert response_update.status_code == 200
    assert response_update.json()["nome"] == "User Teste Alterado"

    response_get = await async_client.get(f"{URL_USER}{user_id}", headers=headers)
    assert response_get.status_code == 200
    assert response_get.json()["nome"] == "User Teste Alterado"

    response_delete = await async_client.delete(f"{URL_USER}{user_id}", headers=headers)
    assert response_delete.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_criar_usuario_exige_autenticacao(async_client):
    """O cadastro público foi fechado junto com o SSO.

    Antes, qualquer um na rede criava conta batendo neste endpoint sem token.
    """
    response = await async_client.post(
        URL_USER, json={"nome": "invasor", "email": "invasor@gmail.com"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_update_other_user_forbidden(async_client, auth, outro_auth):
    other_id = outro_auth["user"]["id"]

    response = await async_client.put(
        f"{URL_USER}{other_id}",
        json={"nome": "hacker"},
        headers=auth["headers"],
    )
    assert response.status_code == 403
