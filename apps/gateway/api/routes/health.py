from api.dependencies import HttpClient, Auth0SettingsDep
from clients.cinema import get_cinema_health
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def get_health(http_client: HttpClient, settings: Auth0SettingsDep) -> dict[str, str]:
    return await get_cinema_health(http_client, settings.cinema_service_url, settings.http_timeout_health_check)
