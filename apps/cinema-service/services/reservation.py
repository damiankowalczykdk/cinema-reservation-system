from decimal import Decimal
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

    async def create_reservation(self, create_reservation: CreateReservation, user_id: str | None = None) -> list[Reservation]:
        screening = await self.screening_repository.get_by_id(create_reservation.screening_id)
        if not screening:
            raise NotFoundException("Screening not found")

        hall = await self.hall_repository.get_by_id(screening.hall_id)
        if not hall:
            raise NotFoundException("Hall not found")

        if bool(user_id) == bool(create_reservation.guest_email):
            raise ValidationException("Provide either user_id or guest_email, not both or neither")

        active_reservation = await self.reservation_repository.get_active_reservation_for_screening(screening.id)

        occupied = {(r.row, r.seat) for r in active_reservation}

        seen: set[tuple[int, int]] = set()

        for s in create_reservation.seats:
            if not (1 <= s.row <= hall.rows and 1 <= s.seat <= hall.seats_per_row):
                raise ValidationException("Seat out of bounds for this hall")
            if (s.row, s.seat) in seen:
                raise ConflictException("Duplicate seat in reservation")
            if (s.row, s.seat) in occupied:
                raise ConflictException("Seat already reserved")
            seen.add((s.row, s.seat))

        group_id = await self.reservation_repository.next_group_id()

        reservations: list[Reservation] = []

        for s in create_reservation.seats:
            reservations.append(Reservation(
                screening_id=screening.id,
                group_id=group_id,
                user_id=user_id,
                guest_email=create_reservation.guest_email,
                guest_name=create_reservation.guest_name,
                row=s.row,
                seat=s.seat,
                status=Status.PENDING,
                price_paid=screening.price

            ))

        return await self.reservation_repository.add_all(reservations)


    async def get_reservations_by_group_id(self, group_id: int) -> Sequence[Reservation]:
        return await self._check_group(group_id)

    async def get_group_total(self, group_id: int) -> Decimal:
        total_price = await self.reservation_repository.get_group_total(group_id)
        if total_price is None:
            raise NotFoundException("Group not found")
        return total_price

    async def get_user_reservations(self, user_id: str | None) -> Sequence[Reservation]:
        if user_id is None:
            raise UnauthorizedException()

        return await self.reservation_repository.get_by_user_id(user_id)


    async def cancel_reservation(
            self,
            group_id: int,
            user_id: str | None,
            is_admin: bool
    ) -> Sequence[Reservation]:

        reservations = await self._check_group(group_id)

        owner_id = reservations[0].user_id
        is_owner = owner_id is not None and owner_id == user_id
        if not (is_admin or is_owner):
            raise NotFoundException("Reservation not allowed")

        for r in reservations:
            if r.status != Status.CANCELLED:
                r.status = Status.CANCELLED

        return await self.reservation_repository.add_all(list(reservations))


    async def delete_reservation_group(self, group_id: int) -> None:
        await self._check_group(group_id)
        await self.reservation_repository.delete_reservation_group(group_id)


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

    async def set_confirm_reservation(self, group_id: int) -> None:
        reservations = await self._check_group(group_id)

        if any(r.status == Status.CANCELLED for r in reservations):
            raise ConflictException("Reservation already cancelled")

        for r in reservations:
            if r.status != Status.CONFIRMED:
                r.status = Status.CONFIRMED

        await self.reservation_repository.add_all(list(reservations))


    async def _check_group(self, group_id: int) -> Sequence[Reservation]:
        reservations = await self.reservation_repository.get_by_group_id(group_id)
        if not reservations:
            raise NotFoundException("Reservation not found")
        return reservations
