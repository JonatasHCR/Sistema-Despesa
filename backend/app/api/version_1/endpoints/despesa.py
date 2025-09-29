from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.despesa import DespesaService
from app.schema.despesa import DespesaSchema, DespesaOutputSchema


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
        self, id: int, db: AsyncSession = Depends(get_db)
    ) -> DespesaOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_id(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto="Despesa"
                ),
            )

    async def _get_all(
        self, limit: int = 15, offset: int = 0, db: AsyncSession = Depends(get_db)
    ) -> list[DespesaOutputSchema]:
        service = self.service(db)
        return await service.get_all(limit, offset)

    async def _create(
        self, schema: DespesaSchema, db: AsyncSession = Depends(get_db)
    ) -> DespesaOutputSchema:
        service = self.service(db)

        return await service.create(schema)

    async def _update(
        self, id: int, schema: DespesaSchema, db: AsyncSession = Depends(get_db)
    ) -> DespesaOutputSchema:
        service = self.service(db)
        try:
            return await service.update(id, schema)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto="Despesa"
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
                    id=id, objeto="Despesa"
                ),
            )

    async def get_by_user_id(
        self, user_id: int, db: AsyncSession = Depends(get_db)
    ) -> list[DespesaOutputSchema]:
        service = self.service(db)
        try:
            return await service.get_by_user_id(user_id)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
