import pytest


URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_create_update_get_delete_user(async_client):
    user_payload = {
        "nome": "usuario teste",
        "email": "teste@gmail.com",
        "senha": "senha123",
    }

    response_create = await async_client.post(URL_USER, json=user_payload)
    assert response_create.status_code == 201, response_create.text
    assert response_create.json()["nome"] == user_payload["nome"]
    user_id = response_create.json()["id"]

    login_response = await async_client.post(
        "/auth/login", json={"nome": user_payload["nome"], "senha": user_payload["senha"]}
    )
    assert login_response.status_code == 200, login_response.text
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

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
async def test_integration_update_other_user_forbidden(async_client, auth):
    # Cria um segundo usuário
    other_payload = {"nome": "outro", "email": "outro@gmail.com", "senha": "outrasenha"}
    other_response = await async_client.post(URL_USER, json=other_payload)
    other_id = other_response.json()["id"]

    response = await async_client.put(
        f"{URL_USER}{other_id}",
        json={"nome": "hacker"},
        headers=auth["headers"],
    )
    assert response.status_code == 403
