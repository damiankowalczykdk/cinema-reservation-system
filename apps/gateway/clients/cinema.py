import httpx
from api.dependencies import HttpClient
from core.config import settings


async def get_cinema_health(client: HttpClient) -> dict:
    try:
        response = await client.get(f"{settings.cinema_service_url}/health", timeout=settings.http_timeout_health_check)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        return {"status": "unreachable", "message": str(e)}
