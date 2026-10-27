from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from activities import ReservationActivities
from core.config import settings


async def test_expire_reservation(
    mock_reservation_activities: ReservationActivities, mock_temporal_client: AsyncMock
) -> None:
    await mock_reservation_activities.expire_reservation(1)

    mock_temporal_client.request.assert_called_once_with(
        "POST", f"{settings.cinema_service_url}/reservation/1/expire"
    )


@patch("activities.send", new_callable=AsyncMock)
async def test_send_email(mock_send: AsyncMock, mock_email_activities) -> None:
    await mock_email_activities._send(
        email="test@example.com", subject="test", body="test", qr_code=b"fake-png"
    )
    mock_send.assert_awaited_once()

    message = mock_send.call_args.args[0]
    res = mock_send.call_args.kwargs

    assert message["To"] == "test@example.com"
    assert message["Subject"] == "test"

    assert res["hostname"] == settings.smtp_host
    assert res["port"] == settings.smtp_port


@patch("activities.send", new_callable=AsyncMock)
async def test_send_tickets(
    mock_send: AsyncMock, mock_email_activities, mock_temporal_client
) -> None:
    mock_temporal_client.request.return_value.json.return_value = {
        "group_id": 42,
        "movie_title": "Test Movie",
        "city": "Test City",
        "start_time": datetime.now(UTC).isoformat(),
        "hall_name": "Test Hall",
        "seats": [{"row": 1, "seat": 1}],
        "total_price": Decimal(25),
        "ticket_code": "42.5FGTEW76",
        "currency": "PLN",
    }

    await mock_email_activities.send_tickets(group_id=42, email="test@example.com")

    mock_send.assert_awaited_once()
    mock_temporal_client.request.assert_called_once_with(
        "GET", f"{settings.cinema_service_url}/reservation/42/summary"
    )

    ticket = mock_send.call_args.args[0]

    assert ticket["To"] == "test@example.com"
