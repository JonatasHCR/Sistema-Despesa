from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schema.user import UserOutputSchema, UserSchema
from app.repository.user import UserRepository
from .base import BaseService


class UserService(BaseService[UserRepository, UserSchema, UserOutputSchema]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository, UserOutputSchema, db)

    async def get_by_email(self, email: str) -> UserOutputSchema:
        busca = await self.repository.get_by_email(email)
        return UserOutputSchema.model_validate(busca)
    
    async def get_by_username(self, username: str) -> UserOutputSchema:
        busca = await self.repository.get_by_username(username)
        return UserOutputSchema.model_validate(busca)

    async def update(self, id: int, schema: UserSchema) -> UserOutputSchema:
        update_data = schema.model_dump(exclude_unset=True)
        
        # If password is not being updated, remove it from the dict
        if not update_data.get('senha'):
            update_data.pop('senha', None)
            
        resposta = await self.repository.update(id, **update_data)

        return self.output_schema.model_validate(resposta)
