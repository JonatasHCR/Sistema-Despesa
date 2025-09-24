import pytest

from app.schema.user import UserSchema
from app.service.user import UserService


user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
    "senha": "senha123criptografada",
}


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_create(async_db):
    service = UserService(async_db)
    resposta = await service.create(UserSchema(**user_teste))
    assert resposta.id is not None


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_id(async_db):
    service = UserService(async_db)
    teste_id = await service.create(UserSchema(**user_teste))

    user = await service.get_by_id(teste_id.id)
    assert user.nome == user_teste["nome"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_email(async_db):
    service = UserService(async_db)
    await service.create(UserSchema(**user_teste))

    user = await service.get_by_email(user_teste["email"])
    user.email == user_teste["email"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_all(async_db):
    service = UserService(async_db)
    await service.create(UserSchema(**user_teste))

    ativos = await service.get_all()
    assert len(ativos) > 0


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_update(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))
    user_id = user.id

    user_teste["nome"] = "Nome Alterado"
    user_teste["email"] = "teste_alterado@gmail.com"

    user_alterado = await service.update(user_id, UserSchema(**user_teste))
    assert user_alterado.nome == user_teste["nome"]
    assert user_alterado.email == user_teste["email"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_delete(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))
    user_id = user.id

    ativo_deletado = await service.delete(user_id)
    assert ativo_deletado is None
