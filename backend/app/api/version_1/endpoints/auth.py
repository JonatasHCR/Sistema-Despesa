
from fastapi import Depends, HTTPException, APIRouter, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token, verify_password
from app.service.user import UserService
from app.schema.user import TokenSchema, UserOutputSchema


class LoginSchema(BaseModel):
    nome: str
    senha: str


class AuthEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["Auth"])
        self.register_routes()

    def register_routes(self):
        # slowapi exige um param `request: Request` na função para extrair o IP.
        limited = limiter.limit("5/minute")(self.login)
        self.router.post(
            "/login", response_model=TokenSchema, status_code=status.HTTP_200_OK
        )(limited)

    async def login(
        self,
        request: Request,
        login_data: LoginSchema,
        db: AsyncSession = Depends(get_db),
    ) -> TokenSchema:
        service = UserService(db)
        user = await service.get_model_by_username(login_data.nome)

        if user is None or not verify_password(login_data.senha, user.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(subject=user.id)
        return TokenSchema(
            access_token=token,
            user=UserOutputSchema.model_validate(user),
        )
