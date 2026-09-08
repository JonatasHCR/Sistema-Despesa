import pytest

from app.schema.user import UserSchema, UserUpdateSchema
from app.service.user import UserService


# Sem `senha`: este serviço não guarda mais credencial nenhuma. Os dois testes
# que verificavam o hash (na criação e na troca) saíram — não há o que hashear,
# e a senha vive só no Keycloak.
user_teste = {
    "nome": "usuario teste",
    "email": "teste@gmail.com",
}


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_create_nao_guarda_senha(async_db):
    service = UserService(async_db)
    resposta = await service.create(UserSchema(**user_teste))
    assert resposta.id is not None

    raw_user = await service.get_model_by_email(user_teste["email"])
    assert raw_user is not None
    # A coluna continua existindo (linhas antigas ainda têm hash), mas nada
    # mais a escreve.
    assert raw_user.senha is None
    assert raw_user.external_id is None


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
async def test_service_update(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))

    alterado = await service.update(user.id, UserUpdateSchema(nome="outro nome"))
    assert alterado.nome == "outro nome"
    assert alterado.email == user_teste["email"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_delete(async_db):
    service = UserService(async_db)
    user = await service.create(UserSchema(**user_teste))

    resultado = await service.delete(user.id)
    assert resultado is None
