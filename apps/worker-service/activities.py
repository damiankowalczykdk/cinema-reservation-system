from datetime import datetime
from decimal import Decimal
from email.message import EmailMessage
import httpx
from temporalio import activity
from core.config import settings
from aiosmtplib import send


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


class EmailActivities:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client



    @activity.defn
    async def send_tickets(self, group_id: int, email: str):

        resp = await self.client.request(
            "GET",
            f"{settings.cinema_service_url}/reservation/{group_id}/summary"
        )
        resp.raise_for_status()

        data = resp.json()

        start_time = datetime.fromisoformat(data["start_time"]).astimezone(settings.WARSAW)
        seats = [f"{chr(ord('A') + seat['row'] - 1)}{seat['seat']}" for seat in data["seats"]]
        seats_text = ", ".join(seats)
        total_text = f"{Decimal(data["total_price"]):.2f} zł".replace(".", ",")
        body = "\n".join([
            f"Kod rezerwacji: {data['group_id']}",
            "",
            data["movie_title"],
            data["city"],
            start_time.strftime("%d.%m.%Y %H:%M"),
            "",
            "Numer sali",
            data["hall_name"],
            "",
            "Twoje miejsca",
            seats_text,
            "",
            "SUMA",
            total_text,
        ])

        await self._send(email=email, subject="Confirmed your reservation", body=body)



    async def _send(self, email: str, subject: str, body: str):

        message = EmailMessage()

        message["From"] = settings.smtp_sender
        message["To"] = email
        message["Subject"] = subject

        message.set_content(body)

        await send(message, hostname=settings.smtp_host, port=settings.smtp_port)