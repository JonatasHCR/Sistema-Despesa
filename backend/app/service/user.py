from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import User
from app.schema.user import UserOutputSchema, UserSchema, UserUpdateSchema
from app.repository.user import UserRepository
from .base import BaseService


class UserService(BaseService[UserRepository, UserSchema, UserUpdateSchema, UserOutputSchema]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository, UserOutputSchema, db)

    async def get_by_email(self, email: str) -> UserOutputSchema:
        busca = await self.repository.get_by_email(email)
        return UserOutputSchema.model_validate(busca)

    async def get_by_username(self, username: str) -> UserOutputSchema | None:
        busca = await self.repository.get_by_username(username)
        if busca is None:
            return None
        return UserOutputSchema.model_validate(busca)

    async def get_model_by_email(self, email: str) -> User | None:
        """Objeto User cru, para o fluxo de autenticação."""
        return await self.repository.find_by_email(email)
