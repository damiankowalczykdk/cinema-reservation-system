from unittest.mock import AsyncMock

from activities import ReservationActivities
from core.config import settings


async def test_expire_reservation(mock_reservation_activities: ReservationActivities, mock_temporal_client: AsyncMock) -> None:
    await mock_reservation_activities.expire_reservation(1)

    mock_temporal_client.request.assert_called_once_with("POST", f"{settings.cinema_service_url}/reservation/1/expire")



