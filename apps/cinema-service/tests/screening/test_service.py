import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from core.exceptions import ConflictException, NotFoundException
from domain.models.hall import Hall
from domain.models.movie import Movie, Genre
from domain.models.screening import Screening
from domain.schemas.screening import CreateScreening, ScreeningRead, UpdateScreening
from services.screening import ScreeningService


@pytest.fixture
def mock_repo_screening() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def mock_repo_movie() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def mock_repo_hall() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def service_screening(
        mock_repo_screening: AsyncMock,
        mock_repo_movie: AsyncMock,
        mock_repo_hall: AsyncMock
) -> ScreeningService:
    return ScreeningService(mock_repo_screening, mock_repo_movie, mock_repo_hall)

async def test_create_screening(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock,
        mock_repo_movie: AsyncMock,
        mock_repo_hall: AsyncMock
) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title2",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=datetime(2026,8,26)
    )

    mock_repo_movie.get_by_id = AsyncMock(return_value=movie)
    mock_repo_hall.get_by_id = AsyncMock(return_value=True)

    create_screening = CreateScreening(
        movie_id=1,
        hall_id=2,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    mock_repo_screening.get_overlapping_screenings = AsyncMock(return_value=None)

    await service_screening.create_screening(create_screening=create_screening)

    mock_repo_screening.add.assert_called_once()

    result = mock_repo_screening.add.call_args[0][0]

    assert result.movie_id == 1


async def test_create_screening_if_overlapping(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock,
        mock_repo_movie: AsyncMock,
        mock_repo_hall: AsyncMock
) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title2",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=datetime(2026,8,26)
    )

    mock_repo_movie.get_by_id = AsyncMock(return_value=movie)
    mock_repo_hall.get_by_id = AsyncMock(return_value=True)

    create_screening = CreateScreening(
        movie_id=1,
        hall_id=2,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    mock_repo_screening.get_overlapping_screenings = AsyncMock(return_value=True)

    with pytest.raises(ConflictException, match="Hall already has a screening at this time"):
        await service_screening.create_screening(create_screening=create_screening)

async def test_get_screening_by_id_success(service_screening: ScreeningService, mock_repo_screening: AsyncMock) -> None:
    screening = ScreeningRead(
        id=1,
        movie_id=1,
        hall_id=2,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)

    result = await service_screening.get_screenings_by_id(1)

    assert result.price == Decimal("19.99")

async def test_get_screening_by_id_not_found(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock
    ) -> None:

    mock_repo_screening.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundException, match="Screening not found"):
        await service_screening._check_screening_by_id(1)

async def test_get_by_id_not_found_movie(
        service_screening: ScreeningService,
        mock_repo_movie: AsyncMock
        ) -> None:

    mock_repo_movie.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Movie not found"):
        await service_screening._check_movie_by_id(1)

async def test_get_by_id_not_found_hall(
        service_screening: ScreeningService,
        mock_repo_hall: AsyncMock
        ) -> None:

    mock_repo_hall.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Hall not found"):
        await service_screening._check_hall_by_id(1)


async def test_delete_screening_by_id_success(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock
        ) -> None:
    mock_repo_screening.delete_by_id = AsyncMock(return_value=True)

    await service_screening.delete_screening_by_id(1)

    mock_repo_screening.delete_by_id.assert_called_once()


async def test_update_screening_success(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock,
        mock_repo_movie: AsyncMock,
        mock_repo_hall: AsyncMock
) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title2",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=datetime(2026,8,26)
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
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_movie.get_by_id = AsyncMock(return_value=movie)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    update = UpdateScreening(

        price=Decimal("29.99")
    )

    mock_repo_screening.get_overlapping_screenings = AsyncMock(return_value=[])

    await service_screening.update_screening(1, update)

    mock_repo_screening.add.assert_called_once()

    result = mock_repo_screening.add.call_args[0][0]

    assert result.price == Decimal("29.99")

    assert repr(screening) == f"< Screening 1 movie 1 hall 1 start_time 2026-08-26 18:00:00 price 29.99 >"

async def test_update_screening_if_overlapping(
        service_screening: ScreeningService,
        mock_repo_screening: AsyncMock,
        mock_repo_movie: AsyncMock,
        mock_repo_hall: AsyncMock
) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title2",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=datetime(2026,8,26)
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
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    screening_2 = Screening(
        id=2,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18, 30, 0),
        price=Decimal("39.99")
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_movie.get_by_id = AsyncMock(return_value=movie)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    update = UpdateScreening(

        price=Decimal("29.99")
    )

    mock_repo_screening.get_overlapping_screenings = AsyncMock(return_value=[screening_2])

    with pytest.raises(ConflictException, match="Hall already has a screening at this time"):
        await service_screening.update_screening(1, update)
