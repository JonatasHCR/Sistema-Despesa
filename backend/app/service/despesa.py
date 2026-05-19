from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.despesa import DespesaOutputSchema, DespesaSchema, DespesaUpdateSchema
from app.repository.despesa import DespesaRepository
from .base import BaseService


class DespesaService(
    BaseService[DespesaRepository, DespesaSchema, DespesaOutputSchema]
):
    def __init__(self, db: AsyncSession):
        super().__init__(DespesaRepository, DespesaOutputSchema, db)

    async def update_partial(self, id: int, schema: DespesaUpdateSchema) -> DespesaOutputSchema:
        data = schema.model_dump(exclude_unset=True, exclude_none=True)
        resposta = await self.repository.update(id, **data)
        return DespesaOutputSchema.model_validate(resposta)

    async def get_by_user_id(self, user_id: int) -> list[DespesaOutputSchema]:
        busca = await self.repository.get_by_user_id(user_id)
        return [DespesaOutputSchema.model_validate(objeto) for objeto in busca]

    async def list_with_user(self, limit: int = 100, offset: int = 0) -> list[DespesaOutputSchema]:
        rows = await self.repository.list_with_user(limit=limit, offset=offset)
        return [
            DespesaOutputSchema.model_validate({
                **{c.name: getattr(despesa, c.name) for c in despesa.__table__.columns},
                "user_nome": user_nome,
            })
            for despesa, user_nome in rows
        ]

    async def create_for_user(self, schema: DespesaSchema, user_id: int) -> DespesaOutputSchema:
        data = schema.model_dump() | {"user_id": user_id}
        resposta = await self.repository.create(**data)
        return DespesaOutputSchema.model_validate(resposta)
