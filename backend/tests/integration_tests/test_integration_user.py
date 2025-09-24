import pytest


user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
    "senha": "senha123criptografada",
}

URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_create_update_get_delete_user(async_client):

    response_create_user = await async_client.post(URL_USER, json=user_teste)
    print(response_create_user.status_code)
    print(response_create_user.text)
    assert response_create_user.status_code == 201
    assert response_create_user.json()["nome"] == user_teste["nome"]
    user_id = response_create_user.json()["id"]

    user_teste["nome"] = "User Teste Alterado"
    response_update_user = await async_client.put(
        f"{URL_USER}{user_id}", json=user_teste
    )
    assert response_update_user.status_code == 200
    assert response_update_user.json()["nome"] == user_teste["nome"]

    response_get_by_id = await async_client.get(f"{URL_USER}{user_id}")
    assert response_get_by_id.status_code == 200
    assert response_get_by_id.json()["nome"] == user_teste["nome"]

    response_delete_user = await async_client.delete(f"{URL_USER}{user_id}")
    assert response_delete_user.status_code == 204
