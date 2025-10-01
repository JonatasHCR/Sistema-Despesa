
from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.service.user import UserService
from app.schema.user import UserOutputSchema


class LoginSchema(BaseModel):
    nome: str
    senha: str


class AuthEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["Auth"])
        self.register_routes()

    def register_routes(self):
        self.router.post(
            "/login", response_model=UserOutputSchema, status_code=status.HTTP_200_OK
        )(self.login)

    async def login(
        self, login_data: LoginSchema, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = UserService(db)
        try:
            user = await service.get_by_username(login_data.nome)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos",
            )

        if not user or user.senha != login_data.senha:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos",
            )

        return user
