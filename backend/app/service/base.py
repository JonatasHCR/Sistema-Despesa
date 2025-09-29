from typing import Generic, TypeVar
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.base import BaseRepository


Repository = TypeVar("Repository", bound=BaseRepository)
OutputSchema = TypeVar("SchemaOutput", bound=BaseModel)
InputShema = TypeVar("SchemaInput", bound=BaseModel)


class BaseService(Generic[Repository, InputShema, OutputSchema]):
    def __init__(self, repository: type[Repository], output_schema: type[OutputSchema], db: AsyncSession):
        self.repository = repository(db)
        self.output_schema = output_schema

    async def get_all(self) -> list[OutputSchema]:
        busca = await self.repository.get_all()

        return [self.output_schema.model_validate(objeto) for objeto in busca]

    async def get_by_id(self, id: int) -> OutputSchema:
        busca = await self.repository.get_by_id(id)

        return self.output_schema.model_validate(busca)

    async def create(self, schema: InputShema) -> OutputSchema:
        resposta = await self.repository.create(**schema.model_dump())

        return self.output_schema.model_validate(resposta)

    async def update(self, id: int, schema: InputShema) -> OutputSchema:
        resposta = await self.repository.update(id, **schema.model_dump())

        return self.output_schema.model_validate(resposta)

    async def delete(self, id: int) -> None:
        await self.repository.delete(id)
