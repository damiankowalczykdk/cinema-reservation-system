import uuid
from datetime import UTC, datetime, timedelta

from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflows import ReservationWorkflow

send_ticket_calls: list[int | str] = []
expire_calls: list[int] = []


@activity.defn(name="send_tickets")
async def fake_send_ticket(group_id: int, email: str) -> None:
    send_ticket_calls.append(group_id)


@activity.defn(name="expire_reservation")
async def fake_expire_cancelled(group_id: int) -> dict[str, str]:
    expire_calls.append(group_id)
    return {"status": "cancelled", "expires_at": ""}


@activity.defn(name="expire_reservation")
async def fake_expire_confirmed(group_id: int) -> dict[str, str]:
    expire_calls.append(group_id)
    return {"status": "confirmed", "expires_at": ""}


@activity.defn(name="expire_reservation")
async def fake_expire_pending_then_cancelled(group_id: int) -> dict[str, str]:
    expire_calls.append(group_id)
    if len(expire_calls) == 1:
        new_expires_at = datetime.now(UTC) + timedelta(minutes=15)
        return {"status": "pending", "expires_at": new_expires_at.isoformat()}
    return {"status": "cancelled", "expires_at": ""}


async def test_workflow_expired(
    workflow_testing: WorkflowEnvironment,
) -> None:
    send_ticket_calls.clear()
    expires_at = await workflow_testing.get_current_time() + timedelta(minutes=15)

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_cancelled, fake_send_ticket],
    ):
        await workflow_testing.client.execute_workflow(
            ReservationWorkflow.run,
            args=[1, expires_at.isoformat(), "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

    assert send_ticket_calls == []
    assert expire_calls == [1]


async def test_workflow_paid_signal(workflow_testing: WorkflowEnvironment) -> None:
    send_ticket_calls.clear()
    expire_calls.clear()
    expires_at = await workflow_testing.get_current_time() + timedelta(minutes=15)

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_cancelled, fake_send_ticket],
    ):
        start_workflow = await workflow_testing.client.start_workflow(
            ReservationWorkflow.run,
            args=[1, expires_at.isoformat(), "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

        await start_workflow.signal(ReservationWorkflow.paid)

        await start_workflow.result()

    assert expire_calls == []
    assert send_ticket_calls == [1]


async def test_workflow_confirmed_without_signal(
    workflow_testing: WorkflowEnvironment,
) -> None:
    send_ticket_calls.clear()
    expire_calls.clear()
    expires_at = await workflow_testing.get_current_time() + timedelta(minutes=15)

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_confirmed, fake_send_ticket],
    ):
        start_workflow = await workflow_testing.client.start_workflow(
            ReservationWorkflow.run,
            args=[1, expires_at.isoformat(), "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

        await start_workflow.result()

    assert expire_calls == [1]
    assert send_ticket_calls == [1]


async def test_workflow_pending_then_cancelled(
    workflow_testing: WorkflowEnvironment,
) -> None:
    send_ticket_calls.clear()
    expire_calls.clear()
    expires_at = await workflow_testing.get_current_time() + timedelta(minutes=15)

    async with Worker(
        client=workflow_testing.client,
        task_queue="test",
        workflows=[ReservationWorkflow],
        activities=[fake_expire_pending_then_cancelled, fake_send_ticket],
    ):
        start_workflow = await workflow_testing.client.start_workflow(
            ReservationWorkflow.run,
            args=[1, expires_at.isoformat(), "test@example.com"],
            id=str(uuid.uuid4()),
            task_queue="test",
        )

        await start_workflow.result()

    assert expire_calls == [1, 1]
    assert send_ticket_calls == []
