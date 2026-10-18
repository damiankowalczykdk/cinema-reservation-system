import httpx
from temporalio import activity

from core.config import settings



class ReservationActivities:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @activity.defn
    async def expire_reservation(self, group_id: int) -> None:

        resp = await self.client.request(
            "POST",
            f"{settings.cinema_service_url}/reservation/{group_id}/expire"
        )

        resp.raise_for_status()

