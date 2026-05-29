
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User:
        user = await self.get_first_by_filter(User.email == email)
        if user is None:
            raise ValueError(f"Usuário com email = {email} não encontrado")
        return user

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_first_by_filter(User.nome == username)
