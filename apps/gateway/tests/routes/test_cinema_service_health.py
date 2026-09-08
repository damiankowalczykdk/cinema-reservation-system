import httpx
import respx
from httpx import AsyncClient, Response

from core.config import Auth0Settings


@respx.mock
async def test_cinema_service_health(client: AsyncClient, test_settings: Auth0Settings) -> None:

    respx.get(f"{test_settings.cinema_service_url}/health").mock(
        return_value=Response(200, json={
            "status": "ok", "message": "cinema-service"
        }))


    response = await client.get("/health")

    assert response.status_code == 200


@respx.mock
async def test_cinema_service_health_unreachable(client: AsyncClient, test_settings: Auth0Settings) -> None:

    respx.get(f"{test_settings.cinema_service_url}/health").mock(side_effect=httpx.ConnectError("boom")
    )


    response = await client.get("/health", timeout=200)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "unreachable"
    assert data["message"] == "boom"


@respx.mock
async def test_cinema_service_health_unhandled_exception(client: AsyncClient, test_settings: Auth0Settings) -> None:

    respx.get(f"{test_settings.cinema_service_url}/health").mock(return_value=Response(
        200, json="error")
    )


    response = await client.get("/health")

    assert response.status_code == 500

    data = response.json()
    assert data["error"] == "INTERNAL_SERVER_ERROR"