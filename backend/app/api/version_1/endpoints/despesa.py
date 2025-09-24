from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.despesa import DespesaService
from app.schema.despesa import DespesaSchema, DespesaOutputSchema
from app.api.version_1.endpoints.base import BaseEndpoint


class DespesaEndpoint(BaseEndpoint[DespesaService, DespesaSchema, DespesaOutputSchema]):
    def __init__(self):
        super().__init__(
            prefix="/despesas",
            service=DespesaService,
            output_schema=DespesaOutputSchema,
            input_schema=DespesaSchema,
            tags=["Despesa"],
        )
        super()._register_routes()
        self.register_routes()

    def register_routes(self):
        self.router.get("/user/{user_id}", response_model=list[DespesaOutputSchema])(
            self.get_by_user_id
        )

    async def get_by_user_id(
        self, user_id: int, db: AsyncSession = Depends(get_db)
    ) -> list[DespesaOutputSchema]:
        service = self.service(db)
        try:
            return await service.get_by_user_id(user_id)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
        
