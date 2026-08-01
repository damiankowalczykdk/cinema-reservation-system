import httpx

from core.config import Auth0Settings
async def get_cinema_health(client: httpx.AsyncClient, settings: Auth0Settings):
    try:
        response = await client.request("GET", f"{settings.cinema_service_url}/health", timeout=5)
        response.raise_for_status()
    except httpx.HTTPError as e:
        return {"status": "unreachable", "message": str(e)}
    return response.json()
