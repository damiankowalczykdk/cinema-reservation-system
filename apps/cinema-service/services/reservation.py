import hashlib
import hmac
import logging
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from core.config import settings
from core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from domain.models.reservation import Reservation, Status
from domain.schemas.reservation import (
    CreateReservation,
    OccupiedSeatsRead,
    ReservationSummaryRead,
    SeatInput,
)
from repositories.hall import HallRepository
from repositories.reservation import ReservationRepository
from repositories.screening import ScreeningRepository
from temporalio.client import Client
from temporalio.service import RPCError

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(
        self,
        reservation_repository: ReservationRepository,
        hall_repository: HallRepository,
        screening_repository: ScreeningRepository,
        temporal_client: Client,
    ) -> None:
        self.reservation_repository = reservation_repository
        self.hall_repository = hall_repository
        self.screening_repository = screening_repository
        self.temporal_client = temporal_client

    async def create_reservation(
        self,
        create_reservation: CreateReservation,
        user_id: str | None = None,
        user_email: str | None = None,
    ) -> list[Reservation]:
        screening = await self.screening_repository.get_by_id(
            create_reservation.screening_id
        )
        if not screening:
            raise NotFoundException("Screening not found")

        if screening.start_time < datetime.now(UTC):
            raise ConflictException(
                "Cannot create reservation screening already started"
            )

        hall = await self.hall_repository.get_by_id(screening.hall_id)
        if not hall:
            raise NotFoundException("Hall not found")

        if bool(user_id) == bool(create_reservation.guest_email):
            raise ValidationException(
                "Provide either user_id or guest_email, not both or neither"
            )

        active_reservation = await self._get_active_reservation_for_screening(
            screening.id
        )

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
            reservations.append(
                Reservation(
                    screening_id=screening.id,
                    group_id=group_id,
                    user_id=user_id,
                    guest_email=create_reservation.guest_email,
                    guest_name=create_reservation.guest_name,
                    row=s.row,
                    seat=s.seat,
                    status=Status.PENDING,
                    price_paid=screening.price,
                    expires_at=datetime.now(UTC)
                    + timedelta(minutes=settings.hold_minutes),
                )
            )

        reservations = await self.reservation_repository.add_all(reservations)

        await self.reservation_repository.commit()

        recipient_email = create_reservation.guest_email or user_email
        expires_at = reservations[0].expires_at.isoformat()

        try:
            await self.temporal_client.start_workflow(
                "ReservationWorkflow",
                id=f"reservations-{group_id}",
                args=[group_id, expires_at, recipient_email],
                task_queue=settings.task_queue,
            )
        except RPCError:
            logger.warning(f"Workflow not started for reservation {group_id}")
        return reservations

    async def get_reservation_summary(self, group_id: int):
        reservation = await self.reservation_repository.get_reservation_summary(
            group_id
        )
        if not reservation:
            raise NotFoundException("Reservation not found")

        res = reservation[0]
        seats = [SeatInput(row=r["row"], seat=r["seat"]) for r in reservation]
        total_price = sum(r["price_paid"] for r in reservation)

        ticket_code = f"{group_id}.{self._sign(group_id)}"

        return ReservationSummaryRead(
            group_id=res["group_id"],
            movie_title=res["movie_title"],
            city=res["city"],
            start_time=res["start_time"],
            hall_name=res["hall_name"],
            seats=seats,
            total_price=Decimal(total_price),
            ticket_code=ticket_code,
            currency=settings.currency,
        )

    async def verify_ticket(self, ticket_code: str) -> ReservationSummaryRead:
        try:
            split = ticket_code.split(".", 1)
            signature = split[1]
            group_id = int(split[0])
        except (ValueError, IndexError):
            raise NotFoundException("Invalid ticket code")

        expected = self._sign(group_id)
        res = hmac.compare_digest(signature.upper().encode(), expected.encode())
        if not res:
            raise NotFoundException("Invalid ticket code")

        reservations = await self._check_group(group_id)
        if any(r.status != Status.CONFIRMED for r in reservations):
            raise ConflictException("Ticket not paid")

        summary = await self.get_reservation_summary(group_id)
        if summary.start_time + timedelta(hours=1) < datetime.now(UTC):
            raise ConflictException("Ticket expired")

        return summary

    async def get_reservations_by_group_id(
        self, group_id: int
    ) -> Sequence[Reservation]:
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

    async def extend(self, group_id: int) -> datetime:
        reservations = await self._check_group(group_id, lock=True)

        now = datetime.now(UTC)
        requested_expires_at = now + timedelta(minutes=settings.extend_minutes)

        for reservation in reservations:
            if reservation.status == Status.CANCELLED:
                raise ConflictException("Cannot extend reservation")
            if reservation.status == Status.CONFIRMED:
                raise ConflictException("Reservation already confirmed")

            max_expires_at = reservation.created_at + timedelta(
                minutes=settings.max_hold_minutes
            )
            new_expires_at = min(requested_expires_at, max_expires_at)

            if reservation.expires_at < now:
                raise ConflictException("Reservation expired")

            reservation.expires_at = new_expires_at

        await self.reservation_repository.add_all(list(reservations))

        await self.reservation_repository.commit()

        return reservations[0].expires_at

    async def expire_group(self, group_id: int) -> list[Reservation]:
        reservations = await self._check_group(group_id, lock=True)

        for r in reservations:
            if r.status == Status.PENDING and r.expires_at < datetime.now(UTC):
                r.status = Status.CANCELLED

        return await self.reservation_repository.add_all(list(reservations))

    async def cancel_reservation(
        self, group_id: int, user_id: str | None, is_admin: bool
    ) -> Sequence[Reservation]:
        reservations = await self._check_group(group_id, lock=True)

        screening_id = reservations[0].screening_id

        screening = await self.screening_repository.get_by_id(screening_id)
        if screening is None:
            raise NotFoundException("Screening not found")

        if screening.start_time < datetime.now(UTC) and not is_admin:
            raise ConflictException(
                "Cannot cancel reservation screening already started"
            )

        owner_id = reservations[0].user_id
        is_owner = owner_id is not None and owner_id == user_id
        if not (is_admin or is_owner):
            raise NotFoundException("Group not found")

        for r in reservations:
            if r.status != Status.CANCELLED:
                r.status = Status.CANCELLED

        res = await self.reservation_repository.add_all(list(reservations))

        await self.reservation_repository.commit()

        await self._cancel_workflow(group_id)

        return res

    async def delete_reservation_group(self, group_id: int) -> None:
        await self._check_group(group_id)
        await self.reservation_repository.delete_reservation_group(group_id)
        await self.reservation_repository.commit()
        await self._cancel_workflow(group_id)

    async def get_occupied_seats(self, screening_id: int) -> OccupiedSeatsRead:
        screening = await self.screening_repository.get_by_id(screening_id)
        if not screening:
            raise NotFoundException("Screening not found")

        hall = await self.hall_repository.get_by_id(screening.hall_id)
        if not hall:
            raise NotFoundException("Hall not found")

        occupied_seats = await self._get_active_reservation_for_screening(screening_id)

        seats = [(r.row, r.seat) for r in occupied_seats]

        return OccupiedSeatsRead(
            seats=seats, row=hall.rows, seat_per_row=hall.seats_per_row
        )

    async def set_confirm_reservation(self, group_id: int) -> None:
        reservations = await self._check_group(group_id, lock=True)

        if any(r.status == Status.CANCELLED for r in reservations):
            raise ConflictException("Reservation already cancelled")

        for r in reservations:
            if r.status != Status.CONFIRMED:
                r.status = Status.CONFIRMED

        await self.reservation_repository.add_all(list(reservations))

    async def _cancel_workflow(self, group_id: int) -> None:
        try:
            await self.temporal_client.get_workflow_handle(
                f"reservations-{group_id}"
            ).cancel()
        except RPCError:
            logger.warning(f"Workflow for group {group_id} not running")

    def _sign(self, group_id: int) -> str:
        signature = hmac.new(
            settings.ticket_secret.encode("utf-8"),
            str(group_id).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature[:16].upper()

    async def _check_group(
        self, group_id: int, lock: bool = False
    ) -> Sequence[Reservation]:
        if not lock:
            reservations = await self.reservation_repository.get_by_group_id(group_id)
        else:
            reservations = await self.reservation_repository.get_by_group_id_for_update(
                group_id
            )

        if not reservations:
            raise NotFoundException("Reservation not found")

        return reservations

    async def _get_active_reservation_for_screening(
        self, screening_id: int
    ) -> Sequence[Reservation]:
        await self.reservation_repository.expire_stale_pending(screening_id)

        active_reservations = (
            await self.reservation_repository.get_active_reservation_for_screening(
                screening_id
            )
        )
        return active_reservations
