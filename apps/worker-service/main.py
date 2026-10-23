import asyncio
import logging

import httpx
from activities import EmailActivities, ReservationActivities
from core.config import settings
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import ReservationWorkflow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main() -> None:
    async with httpx.AsyncClient() as http_client:
        activities = ReservationActivities(http_client)
        email = EmailActivities(http_client)

        client = await Client.connect(settings.temporal_address)

        worker = Worker(
            client=client,
            task_queue=settings.task_queue,
            workflows=[ReservationWorkflow],
            activities=[activities.expire_reservation, email.send_tickets],
        )

        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
