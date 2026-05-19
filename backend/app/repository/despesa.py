from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy import func

from app.model.despesa import Despesa
from app.model.user import User
from app.repository.base import BaseRepository


class DespesaRepository(BaseRepository[Despesa]):
    def __init__(self, db: AsyncSession):
        super().__init__(Despesa, db)
        self._db = db

    async def get_by_user_id(self, user_id: int) -> list[Despesa]:
        return await self.get_by_filter(Despesa.user_id == user_id)

    async def list_with_user(self, limit: int = 100, offset: int = 0) -> list[tuple[Despesa, str]]:
        """Lista despesas + nome do usuário em uma única query (evita N+1 no frontend)."""
        stmt = (
            select(Despesa, User.nome)
            .join(User, User.id == Despesa.user_id)
            .order_by(Despesa.vencimento.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
