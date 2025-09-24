import pytest


despesa_teste = {
    "nome": "usuario teste",
    "tipo": "B",
    "valor": 10.50,
    "vencimento": "2024-12-31",
    "user_id": 1,
}
user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
    "senha": "senha123criptografada",
}

URL_DESPESA = "/despesas/"
URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_create_update_get_delete_despesa(async_client):

    response_create_user = await async_client.post(URL_USER, json=user_teste)
    print(response_create_user.status_code)
    print(response_create_user.text)
    assert response_create_user.status_code == 201
    assert response_create_user.json()["nome"] == user_teste["nome"]
    user_id = response_create_user.json()["id"]
    despesa_teste["user_id"] = user_id

    response_create_despesa = await async_client.post(URL_DESPESA, json=despesa_teste)
    assert response_create_despesa.status_code == 201
    assert response_create_despesa.json()["nome"] == despesa_teste["nome"]
    despesa_id = response_create_despesa.json()["id"]

    despesa_teste["nome"] = "Nome Teste Alterado"
    response_update_despesa = await async_client.put(
        f"{URL_DESPESA}{despesa_id}", json=despesa_teste
    )
    assert response_update_despesa.status_code == 200
    assert response_update_despesa.json()["nome"] == despesa_teste["nome"]

    response_get_despesa = await async_client.get(f"{URL_DESPESA}{despesa_id}")
    assert response_get_despesa.status_code == 200
    assert response_get_despesa.json()["nome"] == despesa_teste["nome"]

    response_get_by_user = await async_client.get(f"{URL_DESPESA}user/{user_id}")
    assert response_get_by_user.status_code == 200

    response_delete_ativo = await async_client.delete(f"{URL_DESPESA}{despesa_id}")
    assert response_delete_ativo.status_code == 204

    response_delete_user = await async_client.delete(f"{URL_USER}{user_id}")
    assert response_delete_user.status_code == 204
