from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, func, RowMapping

from domain.models.cinema import Cinema
from domain.models.hall import Hall
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


    async def get_search_screenings(
            self, movie_id: int | None, cinema_id: int | None, date_from: datetime | None, date_to: datetime | None
    ) -> Sequence[RowMapping]:

        conditions = []

        if movie_id is not None:
            conditions.append(Screening.movie_id == movie_id)

        if cinema_id is not None:
            conditions.append(Hall.cinema_id == cinema_id)

        if date_from is not None:
            conditions.append(Screening.start_time >= date_from)

        if date_to is not None:
            conditions.append(Screening.start_time <= date_to)

        stmt = (
            select(
                Screening.id.label("screening_id"),
                Movie.id.label("movie_id"),
                Movie.title.label("movie_title"),
                Cinema.id.label("cinema_id"),
                Cinema.name.label("cinema_name"),
                Hall.id.label("hall_id"),
                Screening.start_time.label("start_time"),
                Screening.price.label("price")
            )
            .join(Hall, Hall.id == Screening.hall_id)
            .where(
                *conditions
            )
            .join(Movie, Movie.id == Screening.movie_id)
            .join(Cinema, Cinema.id == Hall.cinema_id)

        )
        result = await self.session.execute(stmt)
        return result.mappings().all()

