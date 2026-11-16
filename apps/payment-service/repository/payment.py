from domain.model.payment import Payment, Status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: Payment) -> Payment:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_stripe_session_id(self, stripe_session_id: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.stripe_session_id == stripe_session_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_by_active_group_id(self, group_id: int) -> Payment | None:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.group_id == group_id, Payment.status != Status.FAILED)
            .with_for_update()
        )

        return result.scalar_one_or_none()

    async def update(self, instance: Payment) -> Payment:
        await self.session.flush()
        return instance
