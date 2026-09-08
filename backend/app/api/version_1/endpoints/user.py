
from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.version_1.dependencies import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.service.user import UserService
from app.schema.user import UserSchema, UserOutputSchema, UserUpdateSchema


class UserEndpoint:
    def __init__(self):
        self.service = UserService
        self.router = APIRouter(prefix="/users", tags=["User"])

        self.register_routes()

    def register_routes(self):
        # Nenhuma rota é pública. O cadastro aberto foi fechado junto com o SSO:
        # quem cria conta é o Keycloak, e o provisionamento local acontece
        # sozinho no primeiro login válido (ver `dependencies.get_current_user`).
        self.router.post("/", response_model=UserOutputSchema, status_code=201)(
            self._create
        )
        self.router.put("/{id}", response_model=UserOutputSchema, status_code=200)(
            self._update
        )
        self.router.delete("/{id}", response_model=None, status_code=204)(self._delete)

        self.router.get("/", response_model=list[UserOutputSchema])(self._get_all)
        self.router.get("/{id}", response_model=UserOutputSchema)(self._get_by_id)
        self.router.get("/email/{email}", response_model=UserOutputSchema)(
            self.get_by_email
        )
        self.router.get("/username/{username}", response_model=UserOutputSchema)(
            self.get_by_username
        )

    async def _create(
        self,
        schema: UserSchema,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> UserOutputSchema:
        service = self.service(db)
        return await service.create(schema)

    async def _get_all(
        self,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> list[UserOutputSchema]:
        service = self.service(db)
        return await service.get_all()

    async def _get_by_id(
        self,
        id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_id(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="User"),
            )

    async def _update(
        self,
        id: int,
        schema: UserUpdateSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> UserOutputSchema:
        if current_user.id != id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

        service = self.service(db)
        try:
            return await service.update(id, schema)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="User"),
            )

    async def _delete(
        self,
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> None:
        if current_user.id != id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

        service = self.service(db)
        try:
            return await service.delete(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="User"),
            )

    async def get_by_email(
        self,
        email: str,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_email(email)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error))

    async def get_by_username(
        self,
        username: str,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> UserOutputSchema:
        service = self.service(db)
        user = await service.get_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user
