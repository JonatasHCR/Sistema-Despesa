import pytest

from app.schema.despesa import DespesaSchema
from app.service.despesa import DespesaService


despesa_teste = {
    "nome": "usuario teste",
    "tipo": "B",
    "valor": 10.50,
    "vencimento": "2024-12-31",
    "user_id": 1,
}


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_create(async_db):
    service = DespesaService(async_db)
    resposta = await service.create(DespesaSchema(**despesa_teste))
    assert resposta.id is not None


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_id(async_db):
    service = DespesaService(async_db)
    teste_id = await service.create(DespesaSchema(**despesa_teste))

    despesa = await service.get_by_id(teste_id.id)
    assert despesa.nome == despesa_teste["nome"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_by_user_id(async_db):
    service = DespesaService(async_db)
    await service.create(DespesaSchema(**despesa_teste))

    despesas = await service.get_by_user_id(despesa_teste["user_id"])
    len(despesas) > 0


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_get_all(async_db):
    service = DespesaService(async_db)
    await service.create(DespesaSchema(**despesa_teste))

    ativos = await service.get_all()
    assert len(ativos) > 0


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_update(async_db):
    service = DespesaService(async_db)
    despesa = await service.create(DespesaSchema(**despesa_teste))
    despesa_id = despesa.id

    despesa_teste["nome"] = "Nome Alterado"
    despesa_teste["tipo"] = "N"

    despesa_alterado = await service.update(despesa_id, DespesaSchema(**despesa_teste))
    assert despesa_alterado.nome == despesa_teste["nome"]
    assert despesa_alterado.tipo == despesa_teste["tipo"]


@pytest.mark.asyncio
@pytest.mark.service
async def test_service_delete(async_db):
    service = DespesaService(async_db)
    despesa = await service.create(DespesaSchema(**despesa_teste))
    despesa_id = despesa.id

    ativo_deletado = await service.delete(despesa_id)
    assert ativo_deletado is None
