import httpx
from api.dependencies import HttpClient


async def get_cinema_health(client: HttpClient, cinema_service_url: str, timeout: float) -> dict:
    try:
        response = await client.get(f"{cinema_service_url}/health", timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        return {"status": "unreachable", "message": str(e)}
