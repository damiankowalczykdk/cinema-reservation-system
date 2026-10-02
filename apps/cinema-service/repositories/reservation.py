from datetime import datetime, timezone
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

    async def get_by_group_id_for_update(self, group_id: int) -> Sequence[Reservation]:
        stmt = select(Reservation).where(Reservation.group_id == group_id).order_by(Reservation.id).with_for_update()
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
        stmt = select(Reservation).where(
    Reservation.screening_id == screening_id,
                Reservation.status != Status.CANCELLED
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def  expire_stale_pending(self, screening_id: int) -> None:
        await self.session.execute(
            update(Reservation)
            .where(
                Reservation.screening_id == screening_id,
                Reservation.status == Status.PENDING,
                Reservation.expires_at < datetime.now(timezone.utc)
            )
            .values(status=Status.CANCELLED, updated_at=datetime.now(tz=timezone.utc))
        )

    async def delete_reservation_group(self, group_id: int) -> None:
        stmt = delete(Reservation).where(Reservation.group_id == group_id)
        await self.session.execute(stmt)


