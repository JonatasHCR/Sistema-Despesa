from typing import Type, Generic, TypeVar

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.base import BaseService


Service = TypeVar("Service", bound=BaseService)
InputSchema = TypeVar("InputSchema", bound=BaseModel)
OutputSchema = TypeVar("OutSchema", bound=BaseModel)


class BaseEndpoint(Generic[Service, InputSchema, OutputSchema]):
    router: APIRouter
    service: Type[Service]
    input_schema: Type[InputSchema]
    output_schema: Type[OutputSchema]
    prefix: str
    tags: list[str]

    def __init__(
        self,
        prefix: str,
        service: Type[Service],
        output_schema: Type[OutputSchema],
        input_schema: Type[InputSchema],
        tags: list[str] = None,
    ):
        self.output_schema = output_schema
        self.input_schema = input_schema
        self.prefix = prefix
        self.service = service
        self.router = APIRouter(prefix=prefix, tags=tags or [prefix.strip("/")])


    def _register_routes(self):

        self.router.get("/", response_model=list[self.output_schema])(self._get_all)
        self.router.get("/{id}", response_model=self.output_schema)(self._get_by_id)
        self.router.post("/", response_model=self.output_schema, status_code=201)(
            self._create
        )
        self.router.put("/{id}", response_model=self.output_schema, status_code=200)(
            self._update
        )
        self.router.delete("/{id}", response_model=None, status_code=204)(self._delete)

    async def _get_by_id(
        self, id: int, db: AsyncSession = Depends(get_db)
    ) -> OutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_id(id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto=self.prefix.strip("/").removesuffix("s").capitalize()
                ),
            )

    async def _get_all(
        self, limit: int = 15, offset: int = 0, db: AsyncSession = Depends(get_db)
    ) -> list[OutputSchema]:
        service = self.service(db)
        return await service.get_all(limit, offset)

    async def _create(
        self, schema: Type[InputSchema], db: AsyncSession = Depends(get_db)
    ) -> OutputSchema:
        service = self.service(db)

        return await service.create(schema)

    async def _update(
        self, id: int, schema: InputSchema, db: AsyncSession = Depends(get_db)
    ) -> OutputSchema:
        service = self.service(db)
        try:
            return await service.update(id, schema)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error).format(
                    id=id, objeto=self.prefix.strip("/").removesuffix("s").capitalize()
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
                    id=id, objeto=self.prefix.strip("/").removesuffix("s").capitalize()
                ),
            )
