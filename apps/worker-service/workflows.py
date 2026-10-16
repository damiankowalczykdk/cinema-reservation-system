from datetime import timedelta
from activities import ReservationActivities
from temporalio import workflow


@workflow.defn
class ReservationWorkflow:

    @workflow.run
    async def run(self, group_id: int, hold_minutes: int) -> None:
        workflow.logger.info("Reservation workflow started for group %s hold %s min", group_id, hold_minutes)

        await workflow.sleep(timedelta(minutes=hold_minutes))

        await workflow.execute_activity_method(
            ReservationActivities.expire_reservation,
            group_id,
            start_to_close_timeout=timedelta(seconds=10)
        )