import pytest

from app.core.security import verify_password
from app.schema.user import UserSchema, UserUpdateSchema
from app.service.user import UserService


user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
    "senha": "senha123",
}


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_create_hashes_password(async_db):
    service = UserService(async_db)
    resposta = await service.create(UserSchema(**user_teste))
    assert resposta.id is not None

    # A senha precisa ter virado hash; busca o ORM para verificar.
    raw_user = await service.get_model_by_username(user_teste["nome"])
    assert raw_user is not None
    assert raw_user.senha != user_teste["senha"]
    assert verify_password(user_teste["senha"], raw_user.senha)


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_id(async_db):
    service = UserService(async_db)
    criado = await service.create(UserSchema(**user_teste))

    user = await service.get_by_id(criado.id)
    assert user.nome == user_teste["nome"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_email(async_db):
    service = UserService(async_db)
    await service.create(UserSchema(**user_teste))

    user = await service.get_by_email(user_teste["email"])
    assert user.email == user_teste["email"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_all(async_db):
    service = UserService(async_db)
    await service.create(UserSchema(**user_teste))

    ativos = await service.get_all()
    assert len(ativos) > 0


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_update_rehashes_password(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))

    nova_senha = "nova_senha_super_secreta"
    alterado = await service.update(user.id, UserUpdateSchema(senha=nova_senha))
    assert alterado.nome == user_teste["nome"]

    raw_user = await service.get_model_by_username(user_teste["nome"])
    assert verify_password(nova_senha, raw_user.senha)


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_delete(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))

    resultado = await service.delete(user.id)
    assert resultado is None
