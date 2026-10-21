from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, update, func, delete, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.cinema import Cinema
from domain.models.hall import Hall
from domain.models.movie import Movie
from domain.models.reservation import Reservation, Status, reservation_group_id_seq
from domain.models.screening import Screening
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

    async def get_reservation_summary(self, group_id: int) -> Sequence[RowMapping]:
        stmt = (
            select(
                Reservation.group_id.label('group_id'),
                Movie.title.label('movie_title'),
                Cinema.city.label('city'),
                Screening.start_time.label('start_time'),
                Hall.name.label('hall_name'),
                Reservation.seat.label('seat'),
                Reservation.row.label('row'),
                Reservation.price_paid.label('price_paid')
            )
            .join(Screening, Screening.id == Reservation.screening_id)
            .join(Hall, Hall.id == Screening.hall_id)
            .join(Cinema, Cinema.id == Hall.cinema_id)
            .join(Movie, Movie.id == Screening.movie_id
                  )
            .where(Reservation.group_id == group_id, Reservation.status != Status.CANCELLED)
        ).order_by(Reservation.row, Reservation.seat)

        result = await self.session.execute(stmt)
        return result.mappings().all()

    async def expire_stale_pending(self, screening_id: int) -> None:
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


