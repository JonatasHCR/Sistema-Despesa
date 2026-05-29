from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, insert

from app.model.despesa import Despesa
from app.model.notificacao import DespesaDestinatario
from app.model.user import User
from app.repository.base import BaseRepository


class DespesaRepository(BaseRepository[Despesa]):
    def __init__(self, db: AsyncSession):
        super().__init__(Despesa, db)
        self._db = db

    async def get_by_user_id(self, user_id: int) -> list[Despesa]:
        return await self.get_by_filter(Despesa.user_id == user_id)

    async def create_many(self, rows: list[dict]) -> list[Despesa]:
        """Insere várias despesas em um único commit."""
        objetos = [Despesa(**row) for row in rows]
        self._db.add_all(objetos)
        await self._db.commit()
        for obj in objetos:
            await self._db.refresh(obj)
        return objetos

    # --- Destinatários de notificação ---
    async def existing_user_ids(self, user_ids: list[int]) -> set[int]:
        if not user_ids:
            return set()
        res = await self._db.execute(select(User.id).where(User.id.in_(user_ids)))
        return {row[0] for row in res.all()}

    async def get_destinatarios(self, despesa_id: int) -> list[int]:
        res = await self._db.execute(
            select(DespesaDestinatario.user_id).where(
                DespesaDestinatario.despesa_id == despesa_id
            )
        )
        return [row[0] for row in res.all()]

    async def set_destinatarios(self, despesa_id: int, user_ids: list[int]) -> None:
        """Substitui a lista de destinatários de uma despesa (delete + insert)."""
        await self._db.execute(
            delete(DespesaDestinatario).where(
                DespesaDestinatario.despesa_id == despesa_id
            )
        )
        if user_ids:
            await self._db.execute(
                insert(DespesaDestinatario),
                [{"despesa_id": despesa_id, "user_id": uid} for uid in user_ids],
            )
        await self._db.commit()

    async def add_destinatarios_bulk(self, rows: list[dict]) -> None:
        """Insere vários pares (despesa_id, user_id) em um único commit."""
        if rows:
            await self._db.execute(insert(DespesaDestinatario), rows)
            await self._db.commit()

    async def get_pendentes_para_usuario(self, user_id: int, limite: date) -> list[Despesa]:
        """Despesas pendentes em que o usuário é destinatário e vencimento <= limite."""
        stmt = (
            select(Despesa)
            .join(DespesaDestinatario, DespesaDestinatario.despesa_id == Despesa.id)
            .where(
                DespesaDestinatario.user_id == user_id,
                Despesa.status == "P",
                Despesa.vencimento <= limite,
            )
            .order_by(Despesa.vencimento.asc())
        )
        res = await self._db.execute(stmt)
        return list(res.scalars().all())

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
