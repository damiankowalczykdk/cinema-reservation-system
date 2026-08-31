from datetime import date
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.movie import Movie
from repositories.generic import GenericRepository
from sqlalchemy import select


class MovieRepository(GenericRepository[Movie]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Movie)

    async def get_movie_by_title(self, title: str) -> Sequence[Movie]:
        stmt = select(Movie).where(Movie.title == title)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_movie_by_title_and_release_date(self, title: str, release_date: date) -> Movie | None:
        stmt = select(Movie).where(Movie.title == title, Movie.release_date == release_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


