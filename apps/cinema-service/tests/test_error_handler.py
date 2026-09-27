from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from core.exceptions import ValidationException
from main import app


def test_validation_exception_defaults() -> None:
    exc = ValidationException()

    assert exc.message == "Validation failed"
    assert exc.status_code == 400
    assert exc.error_code == "VALIDATION_ERROR"

async def test_create_cinema_422(client: AsyncClient) -> None:

    response = await client.post("/cinema/", json={
        "name": 1,
        "city": "Test City",
        "address": "Test Address"
    })
    assert response.status_code == 422

    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"


async def test_unhandled_exception_handler(client: AsyncClient) -> None:
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    with patch("services.cinema.CinemaService.get_cinema_by_id", side_effect=Exception("boom")):
        async with AsyncClient(transport=transport, base_url="http://test") as raw_client:
            response = await raw_client.get("/cinema/1")

            assert response.status_code == 500
            assert response.json()["error"] == "INTERNAL_SERVER_ERROR"