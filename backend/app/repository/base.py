from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


Model = TypeVar("Model") # Modelo do banco de dados


class BaseRepository(Generic[Model]):
    def __init__(self, model: type[Model], db: AsyncSession):
        self.model = model
        self.__db = db

    async def get_all(self, limit=15, offset=0) -> list[Model]:
        busca = await self.__db.execute(select(self.model).limit(limit).offset(offset))
        busca = busca.scalars().all()

        return busca

    async def get_by_id(self, id: int) -> Model:
        busca = await self.__db.execute(select(self.model).where(self.model.id == id))
        busca = busca.scalar_one_or_none()

        if busca is None:
            raise ValueError("{objeto} com ID = {id} não encontrado.")

        return busca

    async def get_by_filter(self, *filter, limit=15, offset=0) -> list[Model]:
        busca = await self.__db.execute(
            select(self.model).where(*filter).limit(limit).offset(offset)
        )
        busca = busca.scalars().all()

        return busca

    async def create(self, **data) -> Model:
        obj = self.model(**data)
        self.__db.add(obj)
        await self.__db.commit()
        await self.__db.refresh(obj)
        return obj

    async def update(self, id: int, **data) -> Model:
        obj = await self.get_by_id(id)
        for key, value in data.items():
            setattr(obj, key, value)
        self.__db.add(obj)
        await self.__db.commit()
        await self.__db.refresh(obj)
        return obj

    async def delete(self, id: int) -> None:
        obj = await self.get_by_id(id)
        await self.__db.delete(obj)
        await self.__db.commit()

    