from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from domain.models.movie import Movie
from domain.models.screening import Screening
from repositories.generic import GenericRepository


class ScreeningRepository(GenericRepository[Screening]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Screening)

    async def get_overlapping_screenings(
            self, hall_id: int, start_time: datetime, end_time: datetime
    ) -> Sequence[Screening]:
        existing_end_time = Screening.start_time + func.make_interval(0, 0, 0, 0, 0, Movie.duration_minutes)

        stmt = (
            select(Screening)
            .join(Movie, Movie.id == Screening.movie_id)
            .where(
                Screening.hall_id == hall_id,
                Screening.start_time < end_time,
                existing_end_time > start_time,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()