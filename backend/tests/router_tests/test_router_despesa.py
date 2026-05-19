import pytest


URL_DESPESA = "/despesas/"


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_despesas_by_user_id_requires_auth(async_client):
    response = await async_client.get(f"{URL_DESPESA}user/1")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_despesas_by_user_id(async_client, auth):
    response = await async_client.get(
        f"{URL_DESPESA}user/{auth['user']['id']}", headers=auth["headers"]
    )
    assert response.status_code == 200
