from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.user import UserService
from app.schema.user import UserSchema, UserOutputSchema


class UserEndpoint:
    def __init__(self):
        self.service = UserService
        self.router = APIRouter(prefix="/users", tags=["User"])

        self.register_routes()

    def register_routes(self):
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

    async def _get_by_id(
        self, id: int, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_id(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto="User"
                ),
            )

    async def _get_all(
        self, limit: int = 15, offset: int = 0, db: AsyncSession = Depends(get_db)
    ) -> list[UserOutputSchema]:
        service = self.service(db)
        return await service.get_all(limit, offset)

    async def _create(
        self, schema: UserSchema, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)

        return await service.create(schema)

    async def _update(
        self, id: int, schema: UserSchema, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.update(id, schema)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto="User"
                ),
            )

    async def _delete(self, id: int, db: AsyncSession = Depends(get_db)) -> None:
        service = self.service(db)
        try:
            return await service.delete(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto="User"
                ),
            )

    async def get_by_email(
        self, email: str, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_email(email)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error))

    async def get_by_username(
        self, username: str, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_username(username)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error))
