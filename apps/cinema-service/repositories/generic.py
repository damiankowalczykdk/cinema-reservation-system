from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class GenericRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def add_all(self, instances: list[ModelType]) -> list[ModelType]:
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)


    async def get_all(self) -> Sequence[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def delete_by_id(self, id: int) -> None:
        instance = await self.session.get(self.model, id)
        await self.session.delete(instance)
        await self.session.flush()




