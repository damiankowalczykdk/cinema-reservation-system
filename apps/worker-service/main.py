import asyncio
import logging

import httpx
from temporalio.client import Client
from temporalio.worker import Worker

from activities import ReservationActivities
from core.config import settings
from workflows import ReservationWorkflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def main() -> None:
    async with httpx.AsyncClient() as http_client:
        
        activities = ReservationActivities(http_client)

        client = await Client.connect(
            settings.temporal_address
        )
    
        worker = Worker(
            client=client,
            task_queue=settings.task_queue,
            workflows=[
                ReservationWorkflow
            ],
            activities=[
                activities.expire_reservation
            ]
        )
    
        await worker.run()



if __name__ == "__main__":
    asyncio.run(main())