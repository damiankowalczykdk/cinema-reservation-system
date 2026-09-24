from datetime import timedelta, datetime, timezone
from decimal import Decimal
from typing import Sequence
from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.reservation import Reservation, Status, reservation_group_id_seq
from repositories.generic import GenericRepository


class ReservationRepository(GenericRepository[Reservation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Reservation)


    async def get_by_user_id(self, user_id: str) -> Sequence[Reservation]:
        stmt = select(Reservation).where(Reservation.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_group_id(self, group_id: int) -> Sequence[Reservation]:
        stmt = select(Reservation).where(Reservation.group_id == group_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_group_total(self, group_id: int) -> Decimal | None:
        stmt = (
            select(func.sum(Reservation.price_paid))
            .where(
                Reservation.group_id == group_id,
                Reservation.status == Status.PENDING
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar()

    async def next_group_id(self) -> int:
        return await self.session.scalar(reservation_group_id_seq.next_value())

    async def get_active_reservation_for_screening(self, screening_id: int) -> Sequence[Reservation]:
        reservation_time = timedelta(minutes=1)

        cutoff = datetime.now(tz=timezone.utc) - reservation_time

        await self.session.execute(
            update(Reservation)
            .where(
                Reservation.screening_id == screening_id,
                Reservation.status == Status.PENDING,
                Reservation.created_at < cutoff
            )
            .values(status=Status.CANCELLED, updated_at=datetime.now(tz=timezone.utc))
        )


        stmt = select(Reservation).where(
    Reservation.screening_id == screening_id,
                Reservation.status != Status.CANCELLED
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_reservation_group(self, group_id: int) -> None:
        stmt = delete(Reservation).where(Reservation.group_id == group_id)
        await self.session.execute(stmt)


