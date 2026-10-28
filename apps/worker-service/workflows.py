from datetime import datetime, timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import EmailActivities, ReservationActivities


@workflow.defn
class ReservationWorkflow:
    def __init__(self) -> None:
        self.is_paid = False
        self.expires_at: datetime | None = None

    @workflow.run
    async def run(self, group_id: int, expires_at: str, email: str | None) -> None:
        workflow.logger.info(
            "Reservation workflow started for group %s expires at %s",
            group_id,
            expires_at,
        )

        self.expires_at = datetime.fromisoformat(expires_at)

        while not self.is_paid:
            timeout = self.expires_at - workflow.now()
            if timeout <= timedelta(0):
                result = await workflow.execute_activity_method(
                    ReservationActivities.expire_reservation,
                    args=[group_id],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )
                if result["status"] == "confirmed":
                    self.is_paid = True
                elif result["status"] == "pending":
                    self.expires_at = max(
                        datetime.fromisoformat(result["expires_at"]),
                        workflow.now() + timedelta(seconds=5),
                    )
                    continue
                else:
                    return

            try:
                await workflow.wait_condition(lambda: self.is_paid, timeout=timeout)
            except TimeoutError:
                pass

        if email:
            await workflow.execute_activity_method(
                EmailActivities.send_tickets,
                args=[group_id, email],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

    @workflow.signal
    async def paid(self) -> None:
        self.is_paid = True
