
from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.version_1.dependencies import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.service.despesa import DespesaService
from app.schema.despesa import DespesaSchema, DespesaOutputSchema, DespesaUpdateSchema


class DespesaEndpoint:
    def __init__(self):
        self.service = DespesaService
        self.router = APIRouter(prefix="/despesas", tags=["Despesa"])

        self.register_routes()

    def register_routes(self):
        self.router.post("/", response_model=DespesaOutputSchema, status_code=201)(
            self._create
        )
        self.router.put("/{id}", response_model=DespesaOutputSchema, status_code=200)(
            self._update
        )
        self.router.delete("/{id}", response_model=None, status_code=204)(self._delete)

        self.router.get("/", response_model=list[DespesaOutputSchema])(self._get_all)
        self.router.get("/{id}", response_model=DespesaOutputSchema)(self._get_by_id)
        self.router.get("/user/{user_id}", response_model=list[DespesaOutputSchema])(
            self.get_by_user_id
        )

    async def _get_by_id(
        self,
        id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> DespesaOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_id(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="Despesa"),
            )

    async def _get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> list[DespesaOutputSchema]:
        service = self.service(db)
        return await service.list_with_user(limit=limit, offset=offset)

    async def _create(
        self,
        schema: DespesaSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> DespesaOutputSchema:
        service = self.service(db)
        return await service.create_for_user(schema, user_id=current_user.id)

    async def _update(
        self,
        id: int,
        schema: DespesaUpdateSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> DespesaOutputSchema:
        service = self.service(db)
        try:
            existente = await service.repository.get_by_id(id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error).format(id=id, objeto="Despesa"))

        if existente.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

        try:
            return await service.update_partial(id, schema)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="Despesa"),
            )

    async def _delete(
        self,
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> None:
        service = self.service(db)
        try:
            existente = await service.repository.get_by_id(id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error).format(id=id, objeto="Despesa"))

        if existente.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

        try:
            return await service.delete(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(id=id, objeto="Despesa"),
            )

    async def get_by_user_id(
        self,
        user_id: int,
        db: AsyncSession = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> list[DespesaOutputSchema]:
        service = self.service(db)
        try:
            return await service.get_by_user_id(user_id)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
