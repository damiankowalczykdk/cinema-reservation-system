import pytest
from unittest.mock import AsyncMock, MagicMock
from core.exceptions import ConflictException, NotFoundException
from domain.models.cinema import Cinema
from domain.schemas.cinema import CreateCinema, CinemaRead, UpdateCinema
from services.cinema import CinemaService


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def cinema_service(mock_repo: AsyncMock) -> CinemaService:
    return CinemaService(mock_repo)


async def test_create_cinema_success(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_address = AsyncMock(return_value=None)

    create_cinema = CreateCinema(
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )
    await cinema_service.create_cinema(create_cinema)

    mock_repo.get_by_address.assert_awaited_with("Test Address")
    mock_repo.add.assert_awaited_once()

    result = mock_repo.add.call_args[0][0]

    assert result.name == "Test Cinema"
    assert result.city == "Test City"

async def test_create_cinema_if_exist(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    mock_cinema = MagicMock(spec=Cinema)
    mock_repo.get_by_address = AsyncMock(return_value=mock_cinema)

    with pytest.raises(ConflictException, match="Cinema already exists"):
        create_cinema = CreateCinema(
            name="Test Cinema",
            city="Test City",
            address="Test Address"
        )
        await cinema_service.create_cinema(create_cinema)

async def test_get_cinema_by_id_success(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    cinema = CinemaRead(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )

    mock_repo.get_by_id = AsyncMock(return_value=cinema)

    result = await cinema_service.get_cinema_by_id(1)

    assert result.name == "Test Cinema"

async def test_get_cinema_by_id_not_found(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:

    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Cinema does not exist"):
        await cinema_service.get_cinema_by_id(1)


async def test_get_cinema_by_name_success(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    cinema = CinemaRead(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )

    mock_repo.get_by_name = AsyncMock(return_value=cinema)

    result = await cinema_service.get_cinema_by_name("Test Cinema")

    assert result.name == "Test Cinema"

async def test_get_cinema_by_name_not_found(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:

    mock_repo.get_by_name = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Cinema does not exist"):
        await cinema_service.get_cinema_by_name("Test Cinema")


async def test_update_cinema_success(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    cinema = Cinema(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )

    update_cinema = UpdateCinema(
        name="Test Cinema",
        city="Test City",
        address="Test Address2"
    )
    mock_repo.get_by_id = AsyncMock(return_value=cinema)

    await cinema_service.update_cinema(1, update_cinema)

    mock_repo.add.assert_awaited_once()

    result = mock_repo.add.call_args[0][0]

    assert result.address == "Test Address2"

async def test_update_cinema_not_found(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)
    update_cinema = UpdateCinema(
        name="Test Cinema",
        city="Test City",
        address="Test Address2"
    )
    with pytest.raises(NotFoundException, match="Cinema does not exist"):

        await cinema_service.update_cinema(1, update_cinema)


async def test_delete_cinema_by_id_success(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:
    cinema = CinemaRead(
        id=1,
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )

    mock_repo.get_by_id = AsyncMock(return_value=cinema)

    await cinema_service.delete_cinema_by_id(cinema.id)

    mock_repo.delete_by_id.assert_awaited_once_with(1)

async def test_delete_cinema_by_id_not_found(cinema_service: CinemaService, mock_repo: AsyncMock) -> None:

    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Cinema does not exist"):
        await cinema_service.delete_cinema_by_id(1)















