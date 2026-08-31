from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.cinema import Cinema
from domain.models.hall import Hall
from domain.models.movie import Movie, Genre
from domain.models.screening import Screening
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository
from repositories.movie import MovieRepository
from repositories.screening import ScreeningRepository


async def test_get_overlapping_screenings(db_session: AsyncSession) -> None:
    repo_screening = ScreeningRepository(db_session)
    repo_movie = MovieRepository(db_session)
    repo_hall = HallRepository(db_session)
    repo_cinema = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Cinema",
        city="San Jose",
        address="123 Main Street"
    )

    movie = Movie(
        id=1,
        title="Movie",
        description="Movie description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026, 8, 26)
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026,8,26,18,0,0),
        price=Decimal("100.00")
    )
    _ = await repo_cinema.add(cinema)
    _ = await repo_hall.add(hall)
    _ = await repo_movie.add(movie)
    _ = await repo_screening.add(screening)

    end_time = screening.start_time + timedelta(minutes=movie.duration_minutes)

    result = await repo_screening.get_overlapping_screenings(
        hall_id=hall.id,
        start_time=screening.start_time,
        end_time=end_time
    )

    assert result[0].movie_id == 1

