from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.model.user import User
from app.schema.user import UserOutputSchema, UserSchema, UserUpdateSchema
from app.repository.user import UserRepository
from .base import BaseService


class UserService(BaseService[UserRepository, UserSchema, UserOutputSchema]):
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

    async def get_model_by_username(self, username: str) -> User | None:
        """Retorna o objeto User cru (com hash da senha) para fluxos de autenticação."""
        return await self.repository.get_by_username(username)

    async def create(self, schema: UserSchema) -> UserOutputSchema:
        data = schema.model_dump()
        data["senha"] = hash_password(data["senha"])
        resposta = await self.repository.create(**data)
        return self.output_schema.model_validate(resposta)

    async def update(self, id: int, schema: UserUpdateSchema) -> UserOutputSchema:
        update_data = schema.model_dump(exclude_unset=True)

        if update_data.get("senha"):
            update_data["senha"] = hash_password(update_data["senha"])
        else:
            update_data.pop("senha", None)

        resposta = await self.repository.update(id, **update_data)
        return self.output_schema.model_validate(resposta)
