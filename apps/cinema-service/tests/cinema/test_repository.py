from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.cinema import Cinema
from repositories.cinema import CinemaRepository


async def test_get_by_name(db_session: AsyncSession) -> None:
    repo = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Cinema",
        city="San Jose",
        address="123 Main Street"
    )
    _ = await repo.add(cinema)

    result = await repo.get_by_name("Cinema")

    assert result is not None
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].name == "Cinema"
    assert result[0].city == "San Jose"

async def test_get_by_address(db_session: AsyncSession) -> None:
    repo = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Cinema",
        city="San Jose",
        address="123 Main Street"
    )
    _ = await repo.add(cinema)

    result = await repo.get_by_address("123 Main Street")

    assert result is not None
    assert result.id == 1
    assert result.name == "Cinema"
    assert result.city == "San Jose"

async def test_get_all(db_session: AsyncSession) -> None:
    repo = CinemaRepository(db_session)

    cinema = Cinema(
        id=1,
        name="Cinema",
        city="San Jose",
        address="123 Main Street"
    )

    cinema_2 = Cinema(
        id=2,
        name="Cinema",
        city="San Diego",
        address="456 Main Street"
    )
    _ = await repo.add_all([cinema, cinema_2])

    result = await repo.get_all()

    assert len(result) == 2

