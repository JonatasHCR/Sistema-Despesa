from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.version_1.dependencies import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.schema.notificacao import (
    DigestSchema,
    NotificacaoConfigSchema,
    NotificacaoConfigUpdateSchema,
)
from app.service.notificacao import NotificacaoService


class NotificacaoEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/notificacoes", tags=["Notificacao"])
        self.register_routes()

    def register_routes(self):
        self.router.get("/config", response_model=NotificacaoConfigSchema)(
            self._get_config
        )
        self.router.put("/config", response_model=NotificacaoConfigSchema)(
            self._update_config
        )
        self.router.get("/digest", response_model=DigestSchema)(self._get_digest)

    async def _get_config(
        self,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> NotificacaoConfigSchema:
        return await NotificacaoService(db).get_config(current_user.id)

    async def _update_config(
        self,
        schema: NotificacaoConfigUpdateSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> NotificacaoConfigSchema:
        return await NotificacaoService(db).update_config(current_user.id, schema)

    async def _get_digest(
        self,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> DigestSchema:
        return await NotificacaoService(db).get_digest(current_user.id)
