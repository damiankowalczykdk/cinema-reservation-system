from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.cinema import Cinema
from domain.models.hall import Hall
from domain.models.movie import Movie, Genre
from domain.models.reservation import Reservation, Status
from domain.models.screening import Screening
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository
from repositories.movie import MovieRepository
from repositories.reservation import ReservationRepository
from repositories.screening import ScreeningRepository
from tests.reservation.test_service import reservation_service


async def test_get_user_by_id(db_session: AsyncSession) -> None:
    reservation_repo = ReservationRepository(db_session)
    screening_repo = ScreeningRepository(db_session)
    hall_repo = HallRepository(db_session)
    movie_repo = MovieRepository(db_session)
    cinema_repo = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="123 Main Street"
    )

    await cinema_repo.add(cinema)

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    await hall_repo.add(hall)

    movie = Movie(
        id=1,
        title="Movie",
        description="Movie description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026, 8, 23)
    )

    await movie_repo.add(movie)

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18, 0, 0),
        price=Decimal("19.99")
    )
    await screening_repo.add(screening)

    reservation = Reservation(
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    await reservation_repo.add(reservation)

    result = await reservation_repo.get_user_by_id("test123")

    assert result[0].row == 1
    assert result[0].seat == 1

async def test_get_active_reservation_for_screening(db_session: AsyncSession) -> None:
    reservation_repo = ReservationRepository(db_session)
    screening_repo = ScreeningRepository(db_session)
    hall_repo = HallRepository(db_session)
    movie_repo = MovieRepository(db_session)
    cinema_repo = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="123 Main Street"
    )

    await cinema_repo.add(cinema)

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    await hall_repo.add(hall)

    movie = Movie(
        id=1,
        title="Movie",
        description="Movie description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026, 8, 23)
    )

    await movie_repo.add(movie)

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18, 0, 0),
        price=Decimal("19.99")
    )
    await screening_repo.add(screening)

    reservation = Reservation(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    await reservation_repo.add(reservation)

    result = await reservation_repo.get_active_reservation_for_screening(reservation.id)

    assert result[0].status == Status.PENDING

    assert repr(result) == f"[< Reservation 1 screening 1 row 1 seat 1 status Status.PENDING price 19.99 >]"