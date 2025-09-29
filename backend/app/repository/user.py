from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User:
        busca = await self.get_by_filter(User.email == email)
        if busca:
            return busca[0]

        raise ValueError(f"Usuário com email = {email} não encontrado")
    
    async def get_by_username(self, username: str) -> User:
        busca = await self.get_by_filter(User.nome == username)
        if busca:
            return busca[0]

        raise ValueError(f"Usuário com nome = {username} não encontrado")
