import pytest


URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_users_by_email_requires_auth(async_client):
    response = await async_client.get(f"{URL_USER}email/inexistente@gmail.com")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_users_by_email_returns_404_when_missing(async_client, auth):
    response = await async_client.get(
        f"{URL_USER}email/inexistente@gmail.com", headers=auth["headers"]
    )
    assert response.status_code == 404
