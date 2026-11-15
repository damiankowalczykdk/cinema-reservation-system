import io
from email.message import EmailMessage

import httpx
import qrcode
from aiosmtplib import send
from core.config import settings
from domain.schemas.activities import ReservationSummary
from temporalio import activity


class ReservationActivities:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @activity.defn
    async def expire_reservation(self, group_id: int) -> dict[str, str]:
        resp = await self.client.request(
            "POST", f"{settings.cinema_service_url}/reservation/{group_id}/expire"
        )

        resp.raise_for_status()

        return resp.json()


class EmailActivities:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @activity.defn
    async def send_tickets(self, group_id: int, email: str) -> None:
        data = await self._get_summary(group_id)

        qr_code = self._generate_qr_code(data.ticket_code)

        body = self._build_text(data)

        await self._send(
            email=email,
            subject="Your booking has been confirmed",
            body=body,
            qr_code=qr_code,
        )

    async def _get_summary(self, group_id: int) -> ReservationSummary:
        resp = await self.client.request(
            "GET", f"{settings.cinema_service_url}/reservation/{group_id}/summary"
        )
        resp.raise_for_status()

        return ReservationSummary.model_validate(resp.json())

    async def _send(self, email: str, subject: str, body: str, qr_code: bytes) -> None:
        message = EmailMessage()

        message["From"] = settings.smtp_sender
        message["To"] = email
        message["Subject"] = subject

        message.set_content(body)
        message.add_attachment(
            qr_code, maintype="image", subtype="png", filename="bilety.png"
        )

        await send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
        )

    def _generate_qr_code(self, ticket_code: str) -> bytes:
        qr = qrcode.QRCode(box_size=10, border=5)
        qr.add_data(ticket_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer)

        qr_code = buffer.getvalue()
        return qr_code

    def _build_text(self, data: ReservationSummary) -> str:
        start_time = data.start_time.astimezone(settings.WARSAW)
        seats = [f"{chr(ord('A') + seat.row - 1)}{seat.seat}" for seat in data.seats]
        seats_text = ", ".join(seats)
        total_text = f"{data.total_price:.2f} {data.currency.upper()}".replace(".", ",")
        body = "\n".join(
            [
                f"Kod rezerwacji: {data.ticket_code}",
                "",
                data.movie_title,
                data.city,
                start_time.strftime("%d.%m.%Y %H:%M"),
                "",
                "Numer sali",
                data.hall_name,
                "",
                "Twoje miejsca",
                seats_text,
                "",
                "SUMA",
                total_text,
            ]
        )
        return body
