from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.generic import GenericRepository
from domain.models.cinema import Cinema


class CinemaRepository(GenericRepository[Cinema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cinema)

    async def get_by_name(self, name: str) -> Cinema | None:
        stmt = select(Cinema).where(Cinema.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_address(self, address: str) -> Cinema | None:
        stmt = select(Cinema).where(Cinema.address == address)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

