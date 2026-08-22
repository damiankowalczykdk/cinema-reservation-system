import pytest
from unittest.mock import AsyncMock
from core.exceptions import NotFoundException, ConflictException
from domain.models.cinema import Cinema
from domain.models.hall import Hall
from domain.schemas.hall import CreateHall, HallRead, UpdateHall
from services.hall import HallService


@pytest.fixture
def mock_repo_cinema() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def mock_repo_hall() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def hall_service(mock_repo_hall: AsyncMock, mock_repo_cinema: AsyncMock) -> HallService:
    return HallService(mock_repo_hall, mock_repo_cinema)


async def test_create_hall_success(
        hall_service: HallService,
        mock_repo_hall: AsyncMock,
        mock_repo_cinema: AsyncMock
) -> None:
    mock_repo_cinema.get_by_id.return_value = AsyncMock(return_value=True)

    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=None)

    hall = CreateHall(
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    await hall_service.create_hall(hall)

    mock_repo_hall.add.assert_called_once()
    mock_repo_hall.get_by_cinema_id_and_hall_name.assert_awaited_with(1, "Test Hall")

    result = mock_repo_hall.add.call_args[0][0]
    assert result is not None
    assert result.cinema_id == 1
    assert result.name == "Test Hall"
    assert result.rows == 10




async def test_create_hall_if_not_found_cinema(
        hall_service: HallService,
        mock_repo_cinema: AsyncMock
) -> None:
    mock_repo_cinema.get_by_id = AsyncMock(return_value=None)
    hall = CreateHall(
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    with pytest.raises(NotFoundException, match="Cinema does not exist"):
        await hall_service.create_hall(hall)

async def test_create_hall_if_hall_already_exist(
        hall_service: HallService,
        mock_repo_hall: AsyncMock,
        mock_repo_cinema: AsyncMock
) -> None:
    mock_repo_cinema.get_by_id = AsyncMock(return_value=True)
    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=True)
    hall = CreateHall(
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    with pytest.raises(ConflictException, match="Hall already exists in this cinema"):
        await hall_service.create_hall(hall)


async def test_get_hall_by_id_success(hall_service: HallService, mock_repo_hall: AsyncMock) -> None:
    hall = HallRead(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    result = await hall_service.get_hall_by_id(hall.id)

    assert result.name == "Test Hall"

async def test_get_hall_by_id_not_found(hall_service: HallService, mock_repo_hall: AsyncMock) -> None:
    mock_repo_hall.get_by_id = AsyncMock(return_value=None)

    hall = HallRead(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )
    with pytest.raises(NotFoundException, match="Hall does not exist"):
        await hall_service.get_hall_by_id(hall.id)


async def test_get_hall_by_name_success(hall_service: HallService, mock_repo_hall: AsyncMock) -> None:
    hall = HallRead(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=hall)

    result = await hall_service.get_hall_by_name(hall.id, hall.name)

    assert result.name == "Test Hall"
    assert result.rows == 10


async def test_get_hall_by_name_not_found_hall(hall_service: HallService, mock_repo_hall: AsyncMock) -> None:
    hall = HallRead(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Hall does not exist"):
        await hall_service.get_hall_by_name(hall.id, hall.name)


async def test_update_hall_success(
        hall_service: HallService,
        mock_repo_hall: AsyncMock
) -> None:

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=None)

    updated_hall = UpdateHall(
        name="Updated Hall",
        rows=10,
        seats_per_row=10
    )

    await hall_service.update_hall(hall.id, updated_hall)

    result = mock_repo_hall.add.call_args[0][0]

    assert result.name == "Updated Hall"
    assert result.rows == 10

    assert repr(hall) == f"< Hall: 1 name: Updated Hall rows: 10 seats_per_row: 10 >"

async def test_update_hall_not_found_hall(hall_service: HallService, mock_repo_hall: AsyncMock) -> None:
    mock_repo_hall.get_by_id = AsyncMock(return_value=None)
    updated_hall = UpdateHall(
        name="Updated Hall",
        rows=10,
        seats_per_row=10
    )
    with pytest.raises(NotFoundException, match="Hall does not exist"):
        await hall_service.update_hall(1, updated_hall)


async def test_update_hall_if_hall_exists(
        hall_service: HallService,
        mock_repo_hall: AsyncMock,
) -> None:
    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    hall_2 = Hall(
        id=2,
        cinema_id=1,
        name="Test Hall2",
        rows=10,
        seats_per_row=10
    )
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    mock_repo_hall.get_by_cinema_id_and_hall_name = AsyncMock(return_value=hall_2)

    updated_hall = UpdateHall(
        name="Test Hall2",
        rows=10,
        seats_per_row=10
    )
    with pytest.raises(ConflictException, match="Hall already exists"):
        await hall_service.update_hall(hall.id, updated_hall)


async def test_delete_hall_by_id_success(
        hall_service: HallService,
        mock_repo_hall: AsyncMock
) -> None:

    hall = HallRead(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    await hall_service.delete_hall_by_id(hall.id)

    mock_repo_hall.delete_by_id.assert_awaited_once_with(1)

async def test_delete_hall_not_found_hall(
        hall_service: HallService,
        mock_repo_hall: AsyncMock
) -> None:

    mock_repo_hall.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundException, match="Hall does not exist"):

        await hall_service.delete_hall_by_id(1)

