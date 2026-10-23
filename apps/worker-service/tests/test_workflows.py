import uuid
from datetime import UTC, datetime, timedelta

from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflows import ReservationWorkflow

called: list[int | str] = []


@activity.defn(name="expire_reservation")
async def fake_expire_reservation(group_id: int) -> None:
    called.append(group_id)


@activity.defn(name="send_tickets")
async def fake_send_ticket(group_id: int, email: str) -> None:
    return


async def test_workflow_expires_reservation_after_timeout(
    workflow_testing: WorkflowEnvironment,
) -> None:
    called.clear()

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_reservation, fake_send_ticket],
    ):
        await workflow_testing.client.execute_workflow(
            ReservationWorkflow.run,
            args=[1, 15, "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

    assert called == [1]


async def test_workflow_reservation_paid(workflow_testing: WorkflowEnvironment) -> None:
    called.clear()

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_reservation, fake_send_ticket],
    ):
        start_workflow = await workflow_testing.client.start_workflow(
            ReservationWorkflow.run,
            args=[1, 15, "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

        await start_workflow.signal(ReservationWorkflow.paid)

        await start_workflow.result()

    assert called == []


async def test_workflow_reservation_extended(
    workflow_testing: WorkflowEnvironment,
) -> None:
    called.clear()

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_reservation, fake_send_ticket],
    ):
        start_workflow = await workflow_testing.client.start_workflow(
            ReservationWorkflow.run,
            args=[1, 45, "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

        await start_workflow.signal(
            ReservationWorkflow.extended,
            (datetime.now(UTC) + timedelta(minutes=30)).isoformat(),
        )

        await start_workflow.result()

        assert called == [1]
