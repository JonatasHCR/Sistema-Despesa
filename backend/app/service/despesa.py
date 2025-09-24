from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.despesa import DespesaOutputSchema, DespesaSchema
from app.repository.despesa import DespesaRepository
from .base import BaseService


class DespesaService(
    BaseService[DespesaRepository, DespesaSchema, DespesaOutputSchema]
):
    def __init__(self, db: AsyncSession):
        super().__init__(DespesaRepository, DespesaOutputSchema, db)

    async def get_by_user_id(self, user_id: int) -> list[DespesaOutputSchema]:
        busca = await self.repository.get_by_user_id(user_id)
        return [DespesaOutputSchema.model_validate(objeto) for objeto in busca]
