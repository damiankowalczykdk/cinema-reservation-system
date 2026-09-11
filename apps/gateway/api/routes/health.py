from api.dependencies import HttpClient, AuthSettings
from clients.cinema import get_cinema_health
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def get_health(http_client: HttpClient, settings: AuthSettings) -> dict[str, str]:
    return await get_cinema_health(http_client, settings.cinema_service_url, settings.http_timeout_health_check)
