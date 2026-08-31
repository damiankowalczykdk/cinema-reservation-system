from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.hall import Hall
from repositories.generic import GenericRepository


class HallRepository(GenericRepository[Hall]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Hall)

    async def get_by_cinema_id_and_hall_name(self, cinema_id: int, name: str) -> Hall | None:
        stmt = select(Hall).where(Hall.cinema_id == cinema_id, Hall.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()



