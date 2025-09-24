from sqlalchemy.ext.asyncio import AsyncSession

from app.model.despesa import Despesa
from app.repository.base import BaseRepository


class DespesaRepository(BaseRepository[Despesa]):
    def __init__(self, db: AsyncSession):
        super().__init__(Despesa, db)


    async def get_by_user_id(self, user_id: int) -> list[Despesa]:
        busca = await self.get_by_filter(Despesa.user_id == user_id)
        return busca