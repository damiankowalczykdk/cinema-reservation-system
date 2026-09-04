from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from core.exceptions import NotFoundException, ValidationException, ConflictException, UnauthorizedException
from domain.models.hall import Hall
from domain.models.reservation import Reservation, Status
from domain.models.screening import Screening
from domain.schemas.reservation import CreateReservation, ReservationRead
from services.reservation import ReservationService


@pytest.fixture
def mock_repo_reservation() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def mock_repo_hall() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def mock_repo_screening() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def reservation_service(
        mock_repo_reservation: AsyncMock,
        mock_repo_hall: AsyncMock,
        mock_repo_screening: AsyncMock
) -> ReservationService:
    return ReservationService(mock_repo_reservation, mock_repo_hall, mock_repo_screening)


async def test_create_reservation_success(
        reservation_service: ReservationService,
        mock_repo_screening: AsyncMock,
        mock_repo_reservation: AsyncMock,
        mock_repo_hall:AsyncMock
) -> None:

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    create_reservation = CreateReservation(
        screening_id=1,
        row=1,
        seat=1
    )

    await reservation_service.create_reservation(create_reservation, user_id="test123")

    mock_repo_reservation.add.assert_called_once()

async def test_create_reservation_not_found_screening(
        reservation_service: ReservationService,
        mock_repo_screening: AsyncMock,
) -> None:
    mock_repo_screening.get_by_id = AsyncMock(return_value=None)

    create_reservation = CreateReservation(
        screening_id=1,
        row=1,
        seat=1
    )

    with pytest.raises(NotFoundException, match="Screening not found"):
        await reservation_service.create_reservation(create_reservation, user_id="test123")

async def test_create_reservation_not_found_hall(
        reservation_service: ReservationService,
        mock_repo_hall:AsyncMock
) -> None:
    mock_repo_hall.get_by_id = AsyncMock(return_value=None)

    create_reservation = CreateReservation(
        screening_id=1,
        row=1,
        seat=1
    )

    with pytest.raises(NotFoundException, match="Hall not found"):
        await reservation_service.create_reservation(create_reservation, user_id="test123")

async def test_create_reservation_if_provide_user_id_and_guest_email(
        reservation_service: ReservationService,
        mock_repo_screening: AsyncMock,
        mock_repo_reservation: AsyncMock,
        mock_repo_hall:AsyncMock
) -> None:

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    create_reservation = CreateReservation(
        screening_id=1,
        row=1,
        seat=1,
        guest_email="test@example.com"
    )

    with pytest.raises(ValidationException, match="Provide either user_id or guest_email, not both or neither"):
        await reservation_service.create_reservation(create_reservation, user_id="test123")


async def test_create_reservation_if_not_valid_seat(
        reservation_service: ReservationService,
        mock_repo_screening: AsyncMock,
        mock_repo_reservation: AsyncMock,
        mock_repo_hall:AsyncMock
) -> None:

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    create_reservation = CreateReservation(
        screening_id=1,
        row=15,
        seat=1
    )


    with pytest.raises(ValidationException, match="Seat out of bounds for this hall"):
        await reservation_service.create_reservation(create_reservation)

async def test_create_reservation_if_seat_already_reserved(
        reservation_service: ReservationService,
        mock_repo_screening: AsyncMock,
        mock_repo_reservation: AsyncMock,
        mock_repo_hall:AsyncMock
) -> None:

    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18,0,0),
        price=Decimal("19.99")
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    create_reservation = CreateReservation(
        screening_id=1,
        row=1,
        seat=1
    )

    await reservation_service.create_reservation(create_reservation, user_id="test123")

    create_reservation_2 = CreateReservation(
        screening_id=1,
        row=1,
        seat=1,
        guest_email="test@example.com"
    )

    existing_reservation = Reservation(
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_active_reservation_for_screening = AsyncMock(return_value=[existing_reservation])

    with pytest.raises(ConflictException, match="Seat already reserved"):
        await reservation_service.create_reservation(create_reservation_2)


async def test_get_user_reservations_success(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
) -> None:

    reservation = ReservationRead(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_user_by_id = AsyncMock(return_value=[reservation])

    result = await reservation_service.get_user_reservations(user_id=reservation.user_id)

    assert result[0].user_id == "test123"


async def test_get_user_reservations_if_unauthorized(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock
) -> None:
    reservation = ReservationRead(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_user_by_id = AsyncMock(return_value=[reservation])

    with pytest.raises(UnauthorizedException):
        await reservation_service.get_user_reservations(user_id=None)


async def test_cancel_reservation_success(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
) -> None:
    reservation = ReservationRead(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_by_id = AsyncMock(return_value=reservation)

    await reservation_service.cancel_reservation(1, "test123", False)

    result = mock_repo_reservation.add.call_args[0][0]

    assert result.status == Status.CANCELLED


async def test_cancel_reservation_not_allowed(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
) -> None:
    reservation = ReservationRead(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_by_id = AsyncMock(return_value=reservation)

    with pytest.raises(NotFoundException, match="Reservation not allowed"):
        await reservation_service.cancel_reservation(1, "test1234", False)


async def test_delete_by_id_success(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
) -> None:
    reservation = ReservationRead(
        id=1,
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        status=Status.PENDING,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_by_id = AsyncMock(return_value=reservation)

    await reservation_service.delete_reservation_by_id(reservation.id)

    mock_repo_reservation.delete_by_id.assert_called_once_with(reservation.id)

async def test_check_reservation(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock
) -> None:
    mock_repo_reservation.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Reservation not found"):
        await reservation_service._check_reservation(1)


async def test_occupied_seats_success(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
        mock_repo_screening: AsyncMock,
        mock_repo_hall: AsyncMock
    ) -> None:
    screening = Screening(
        id=1,
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 8, 26, 18, 0, 0),
        price=Decimal("19.99")
    )

    hall = Hall(
        id=1,
        cinema_id=1,
        name="Test Hall",
        rows=10,
        seats_per_row=10
    )

    mock_repo_screening.get_by_id = AsyncMock(return_value=screening)
    mock_repo_hall.get_by_id = AsyncMock(return_value=hall)

    reservation = Reservation(
        screening_id=1,
        user_id="test123",
        row=1,
        seat=1,
        price_paid=Decimal("19.99")
    )

    mock_repo_reservation.get_active_reservation_for_screening = AsyncMock(return_value=[reservation])

    result = await reservation_service.get_occupied_seats(screening.id)

    assert result.seats == [(1,1)]


async def test_occupied_seats_not_found_screening(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
        mock_repo_screening: AsyncMock
    ) -> None:

    mock_repo_screening.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Screening not found"):

        await reservation_service.get_occupied_seats(1)


async def test_occupied_seats_not_found_hall(
        reservation_service: ReservationService,
        mock_repo_reservation: AsyncMock,
        mock_repo_hall: AsyncMock
    ) -> None:

    mock_repo_hall.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Hall not found"):

        await reservation_service.get_occupied_seats(1)

