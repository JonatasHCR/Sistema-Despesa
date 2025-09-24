import pytest


user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
    "senha": "senha123criptografada",
}


URL_USER = "/users/"


@pytest.mark.asyncio
@pytest.mark.routers
async def test_get_users_by_email(async_client):
    response = await async_client.get(f"{URL_USER}email/{user_teste['email']}")
    assert response.status_code == 404
