import pytest


despesa_teste = {
    "nome": "usuario teste",
    "tipo": "B",
    "valor": 10.50,
    "vencimento": "2024-12-31",
    "user_id": 1,
}

URL_DESPESA = "/despesas/"


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_despesas_by_user_id(async_client):
    response = await async_client.get(
        f"{URL_DESPESA}user/{despesa_teste['user_id']}"
    )
    assert response.status_code == 200
