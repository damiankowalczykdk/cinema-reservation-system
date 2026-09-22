from datetime import timedelta, datetime, timezone
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.reservation import Reservation, Status
from repositories.generic import GenericRepository


class ReservationRepository(GenericRepository[Reservation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Reservation)


    async def get_user_by_id(self, user_id: str) -> Sequence[Reservation]:
        stmt = select(Reservation).where(Reservation.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


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

