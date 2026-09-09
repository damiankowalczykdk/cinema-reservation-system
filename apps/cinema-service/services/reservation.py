from typing import Sequence
from core.exceptions import NotFoundException, ValidationException, ConflictException, UnauthorizedException
from domain.models.reservation import Reservation, Status
from domain.schemas.reservation import CreateReservation, OccupiedSeatsRead
from repositories.hall import HallRepository
from repositories.reservation import ReservationRepository
from repositories.screening import ScreeningRepository


class ReservationService:
    def __init__(
            self,
            reservation_repository: ReservationRepository,
            hall_repository: HallRepository,
            screening_repository: ScreeningRepository
    ) -> None:
        self.reservation_repository = reservation_repository
        self.hall_repository = hall_repository
        self.screening_repository = screening_repository

    async def create_reservation(self, create_reservation: CreateReservation, user_id: str | None = None) -> Reservation:
        screening = await self.screening_repository.get_by_id(create_reservation.screening_id)
        if not screening:
            raise NotFoundException("Screening not found")

        hall = await self.hall_repository.get_by_id(screening.hall_id)
        if not hall:
            raise NotFoundException("Hall not found")

        is_valid_seat =  1 <= create_reservation.row <= hall.rows and 1 <= create_reservation.seat <= hall.seats_per_row
        if not is_valid_seat:
            raise ValidationException("Seat out of bounds for this hall")

        if bool(user_id) == bool(create_reservation.guest_email):
            raise ValidationException("Provide either user_id or guest_email, not both or neither")

        active_reservation = await self.reservation_repository.get_active_reservation_for_screening(screening.id)

        if any(r.row == create_reservation.row and r.seat == create_reservation.seat for r in active_reservation):
            raise ConflictException("Seat already reserved")

        reservation = Reservation(
            screening_id=create_reservation.screening_id,
            user_id=user_id,
            guest_email=create_reservation.guest_email,
            guest_name=create_reservation.guest_name,
            row=create_reservation.row,
            seat=create_reservation.seat,
            status=Status.PENDING,
            price_paid=screening.price
        )

        return await self.reservation_repository.add(reservation)


    async def get_reservation_by_id(self, reservation_id: int) -> Reservation:
        return await self._check_reservation(reservation_id)


    async def get_user_reservations(self, user_id: str | None) -> Sequence[Reservation]:
        if user_id is None:
            raise UnauthorizedException()

        return await self.reservation_repository.get_user_by_id(user_id)


    async def cancel_reservation(
            self,
            reservation_id: int,
            user_id: str | None,
            is_admin: bool
    ) -> Reservation:

        reservation = await self._check_reservation(reservation_id)

        is_owner = reservation.user_id is not None and reservation.user_id == user_id
        if not(is_admin or is_owner):
            raise NotFoundException("Reservation not allowed")

        if reservation.status != Status.CANCELLED:
            reservation.status = Status.CANCELLED

        return await self.reservation_repository.add(reservation)


    async def delete_reservation_by_id(self, reservation_id: int) -> None:
        await self._check_reservation(reservation_id)
        await self.reservation_repository.delete_by_id(reservation_id)


    async def get_occupied_seats(self, screening_id: int) -> OccupiedSeatsRead:
        screening = await self.screening_repository.get_by_id(screening_id)
        if not screening:
            raise NotFoundException("Screening not found")

        hall = await self.hall_repository.get_by_id(screening.hall_id)
        if not hall:
            raise NotFoundException("Hall not found")

        occupied_seats = await self.reservation_repository.get_active_reservation_for_screening(screening_id)


        seats = [(r.row, r.seat) for r in occupied_seats]

        return OccupiedSeatsRead(seats=seats, row=hall.rows, seat_per_row=hall.seats_per_row)



    async def _check_reservation(self, reservation_id: int) -> Reservation:
        reservation = await self.reservation_repository.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundException("Reservation not found")
        return reservation
