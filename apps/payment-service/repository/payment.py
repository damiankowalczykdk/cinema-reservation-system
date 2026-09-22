from typing import Sequence
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.model.payment import Payment, Status


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: Payment) -> Payment:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def add_all(self, instances: list[Payment]) -> list[Payment]:
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def get_by_id(self, id: int) -> Payment | None:
        return await self.session.get(Payment, id)


    async def get_by_stripe_session_id(self, stripe_session_id: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.stripe_session_id == stripe_session_id))
        return result.scalar_one_or_none()


    async def get_by_active_reservation_id(self, reservation_id: int) -> Payment | None:
        result = await self.session.execute(select(Payment)
            .where(Payment.reservation_id == reservation_id, Payment.status != Status.FAILED))
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Payment]:
        result = await self.session.execute(select(Payment))
        return result.scalars().all()

    async def update(self, instance: Payment) -> Payment:
        await self.session.flush()
        return instance

    async def delete_by_id(self, id: int) -> None:
        instance = await self.session.get(Payment, id)
        await self.session.delete(instance)
        await self.session.flush()




