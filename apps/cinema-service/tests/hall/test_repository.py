from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.cinema import Cinema
from domain.models.hall import Hall
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository


async def test_get_by_cinema_id_and_hall_name(db_session: AsyncSession) -> None:
    repo_hall = HallRepository(db_session)
    repo_cinema = CinemaRepository(db_session)

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    cinema = Cinema(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="123 Main Street"
    )
    _ = await repo_cinema.add(cinema)
    _ = await repo_hall.add(hall)

    result = await repo_hall.get_by_cinema_id_and_hall_name(1, "Test Hall")

    assert result is not None
    assert result.name == "Test Hall"


