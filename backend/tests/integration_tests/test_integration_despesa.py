import pytest


URL_DESPESA = "/despesas/"


despesa_teste = {
    "nome": "usuario teste",
    "tipo": "B",
    "status": "P",
    "valor": 10.50,
    "vencimento": "2024-12-31",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_create_update_get_delete_despesa(async_client, auth):
    headers = auth["headers"]

    response_create = await async_client.post(URL_DESPESA, json=despesa_teste, headers=headers)
    assert response_create.status_code == 201, response_create.text
    body = response_create.json()
    assert body["nome"] == despesa_teste["nome"]
    assert body["user_id"] == auth["user"]["id"]
    despesa_id = body["id"]

    response_update = await async_client.put(
        f"{URL_DESPESA}{despesa_id}",
        json={**despesa_teste, "nome": "Nome Alterado"},
        headers=headers,
    )
    assert response_update.status_code == 200
    assert response_update.json()["nome"] == "Nome Alterado"

    response_get = await async_client.get(f"{URL_DESPESA}{despesa_id}", headers=headers)
    assert response_get.status_code == 200

    response_get_by_user = await async_client.get(
        f"{URL_DESPESA}user/{auth['user']['id']}", headers=headers
    )
    assert response_get_by_user.status_code == 200

    response_delete = await async_client.delete(f"{URL_DESPESA}{despesa_id}", headers=headers)
    assert response_delete.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_can_edit_other_users_despesa(async_client, auth, outro_auth):
    # Sistema usado apenas por pessoas do mesmo setor: qualquer usuário
    # autenticado pode editar despesas de outro usuário.
    create_response = await async_client.post(URL_DESPESA, json=despesa_teste, headers=auth["headers"])
    despesa_id = create_response.json()["id"]

    # O usuário B chega pelo Keycloak, provisionado na primeira chamada.
    other_headers = outro_auth["headers"]

    # User B edita a despesa do A com sucesso
    response = await async_client.put(
        f"{URL_DESPESA}{despesa_id}",
        json={**despesa_teste, "nome": "compartilhada"},
        headers=other_headers,
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "compartilhada"
