from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.movie import Movie, Genre
from repositories.movie import MovieRepository


async def test_get_movie_by_title(db_session: AsyncSession) -> None:
    repo = MovieRepository(db_session)

    movie = Movie(
        id=1,
        title="Movie",
        description="Movie description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8, 23)
    )

    _ = await repo.add(movie)

    result = await repo.get_movie_by_title(movie.title)

    assert result is not None
    assert result[0].title == "Movie"

async def test_get_movie_by_title_and_release_date(db_session: AsyncSession) -> None:
    repo = MovieRepository(db_session)

    movie = Movie(
        id=1,
        title="Movie",
        description="Movie description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8, 23)
    )

    _ = await repo.add(movie)

    result = await repo.get_movie_by_title_and_release_date(movie.title, movie.release_date)
    assert result is not None

    assert result.description == "Movie description"