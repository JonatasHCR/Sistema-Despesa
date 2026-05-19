import pytest

from app.schema.despesa import DespesaSchema
from app.schema.user import UserSchema
from app.service.despesa import DespesaService
from app.service.user import UserService


despesa_teste = {
    "nome": "usuario teste",
    "tipo": "B",
    "status": "P",
    "valor": 10.50,
    "vencimento": "2024-12-31",
}

user_teste = {
    "nome": "dono despesa",
    "email": "dono@gmail.com",
    "senha": "senha123",
}


async def _make_user(async_db) -> int:
    user_service = UserService(async_db)
    user = await user_service.create(UserSchema(**user_teste))
    return user.id


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_create(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    resposta = await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)
    assert resposta.id is not None
    assert resposta.user_id == user_id


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_id(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    criada = await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)

    despesa = await service.get_by_id(criada.id)
    assert despesa.nome == despesa_teste["nome"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_user_id(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)

    despesas = await service.get_by_user_id(user_id)
    assert len(despesas) > 0


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_all_joined(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)

    ativos = await service.list_with_user(limit=10, offset=0)
    assert len(ativos) > 0
    assert ativos[0].user_nome == user_teste["nome"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_update(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    despesa = await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)

    alterado = await service.update(despesa.id, DespesaSchema(**{**despesa_teste, "nome": "Nome Alterado", "tipo": "N"}))
    assert alterado.nome == "Nome Alterado"
    assert alterado.tipo == "N"


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_delete(async_db):
    user_id = await _make_user(async_db)
    service = DespesaService(async_db)
    despesa = await service.create_for_user(DespesaSchema(**despesa_teste), user_id=user_id)

    resultado = await service.delete(despesa.id)
    assert resultado is None
