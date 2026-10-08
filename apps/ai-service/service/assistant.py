from zoneinfo import ZoneInfo

from core.http_client import ServiceRequestClient
from domain.schemas.assistant import ShowtimeRead

WARSAW = ZoneInfo("Europe/Warsaw")


class AssistantService:
    def __init__(self, cinema_client: ServiceRequestClient) -> None:
        self.cinema_client = cinema_client


    async def search_showtimes(self, city: str, genre: str | None, after: str | None, before: str | None) -> list[ShowtimeRead]:

        params = {
            "city": city,
            "genre": genre,
            "date_from": after,
            "date_to": before
        }
        params = {k: v for k, v in params.items() if v is not None}

        responses: list[dict[str, object]] = await self.cinema_client.request(
            "GET",
            f"/screening/search",
            params=params,

        )

        return [ShowtimeRead.model_validate(s) for s in responses]
