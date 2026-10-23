from zoneinfo import ZoneInfo

from core.http_client import ServiceRequestClient
from domain.schemas.assistant import (
    CreateReservation,
    ReservationRead,
    SeatMapRead,
    ShowtimeRead,
)

WARSAW = ZoneInfo("Europe/Warsaw")


class AssistantService:
    def __init__(self, cinema_client: ServiceRequestClient) -> None:
        self.cinema_client = cinema_client

    async def search_showtimes(
        self, city: str, genre: str | None, after: str | None, before: str | None
    ) -> list[ShowtimeRead]:
        params = {"city": city, "genre": genre, "date_from": after, "date_to": before}
        params = {k: v for k, v in params.items() if v is not None}

        responses: list[dict[str, object]] = await self.cinema_client.request(
            "GET",
            "/screening/search",
            params=params,
        )

        return [ShowtimeRead.model_validate(s) for s in responses]

    async def create_reservation(
        self,
        create_reservation: CreateReservation,
        user_id: str | None = None,
        user_email: str | None = None,
    ) -> list[ReservationRead]:
        headers: dict[str, str] | None = None
        if user_id:
            headers = {"X-User-Id": user_id}
            if user_email:
                headers["X-User-Email"] = user_email

        responses: list[dict[str, object]] = await self.cinema_client.request(
            "POST",
            "/reservation/",
            json=create_reservation.model_dump(),
            headers=headers,
        )

        return [ReservationRead.model_validate(r) for r in responses]

    async def get_seats_map(self, screening_id: int) -> SeatMapRead:
        response: dict[str, object] = await self.cinema_client.request(
            "GET",
            f"/reservation/screening/{screening_id}/seats",
        )

        return SeatMapRead.model_validate(response)
