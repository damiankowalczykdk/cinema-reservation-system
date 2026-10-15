import pytest
from unittest.mock import AsyncMock
from domain.schemas.assistant import CreateReservation, SeatInput
from service.assistant import AssistantService


@pytest.fixture
def assistant_service(fake_cinema_client: AsyncMock) -> AssistantService:
    return AssistantService(cinema_client=fake_cinema_client)

@pytest.fixture
def assistant_service_reservation(fake_cinema_client_reservation_read: AsyncMock) -> AssistantService:
    return AssistantService(cinema_client=fake_cinema_client_reservation_read)

@pytest.fixture
def assistant_service_seat_map(fake_cinema_client_seat_map: AsyncMock) -> AssistantService:
    return AssistantService(cinema_client=fake_cinema_client_seat_map)


async def test_search_showtimes(assistant_service: AssistantService) -> None:


    result = await assistant_service.search_showtimes(city="Test City", genre=None, after=None, before=None)

    assert result is not None

    assert result[0].price == 100

async def test_create_reservation(assistant_service_reservation: AssistantService) -> None:
    create_reservation = CreateReservation(
        screening_id=1,
        seats=[SeatInput(row=1, seat=1)],
        guest_email="test@example.com"
    )
    result = await assistant_service_reservation.create_reservation(create_reservation)

    assert result is not None

    assert len(result) ==1
    assert result[0].screening_id == 1
    assert result[0].row == 1


async def test_get_seat_map(assistant_service_seat_map: AssistantService) -> None:

    result = await assistant_service_seat_map.get_seats_map(1)

    assert result.row == 1
    assert result.seat_per_row == 1


