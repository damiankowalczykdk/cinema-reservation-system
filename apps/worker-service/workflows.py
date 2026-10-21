import asyncio
from datetime import timedelta, datetime
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import ReservationActivities, EmailActivities


@workflow.defn
class ReservationWorkflow:
    def __init__(self) -> None:
        self.is_paid = False
        self.expires_at: datetime | None = None
        self.is_extended = False

    @workflow.run
    async def run(self, group_id: int, hold_minutes: float, email: str | None) -> None:
        workflow.logger.info("Reservation workflow started for group %s hold %s min", group_id, hold_minutes)

        if self.expires_at is None:
            self.expires_at = workflow.now() + timedelta(minutes=hold_minutes)


        while not self.is_paid:
            timeout = self.expires_at - workflow.now()
            if timeout <= timedelta(0):
                await workflow.execute_activity_method(
                    ReservationActivities.expire_reservation,
                    args=[group_id],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=3)
                )
                return

            self.is_extended = False

            try:
                await workflow.wait_condition(lambda: self.is_paid or self.is_extended, timeout=timeout)
            except asyncio.TimeoutError:
                pass

        if email:
            await workflow.execute_activity_method(
                EmailActivities.send_tickets,
                args=[group_id, email],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )


    @workflow.signal
    async def paid(self) -> None:
        self.is_paid = True

    @workflow.signal
    async def extended(self, expires_at: str) -> None:
        self.expires_at = datetime.fromisoformat(expires_at)
        self.is_extended = True