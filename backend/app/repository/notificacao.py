from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.notificacao import NotificacaoConfig
from app.repository.base import BaseRepository


class NotificacaoConfigRepository(BaseRepository[NotificacaoConfig]):
    def __init__(self, db: AsyncSession):
        super().__init__(NotificacaoConfig, db)
        self._db = db

    async def get_by_user(self, user_id: int) -> NotificacaoConfig | None:
        res = await self._db.execute(
            select(NotificacaoConfig).where(NotificacaoConfig.user_id == user_id)
        )
        return res.scalar_one_or_none()

    async def update_by_user(self, user_id: int, **data) -> NotificacaoConfig:
        config = await self.get_by_user(user_id)
        for key, value in data.items():
            if value is not None:
                setattr(config, key, value)
        self._db.add(config)
        await self._db.commit()
        await self._db.refresh(config)
        return config
