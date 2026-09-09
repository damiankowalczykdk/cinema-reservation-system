import respx
from httpx import AsyncClient, Response
from core.config import Auth0Settings
from domain.schemas.cinema import CreateCinema, UpdateCinema
from tests.conftest import admin_client


@respx.mock
async def test_create_cinema(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateCinema(
        name="Test Cinema",
        city="Test City",
        address="Test Address"
    )

    respx.post(f"{test_settings.cinema_service_url}/cinema/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "name": "Test Cinema",
            "city": "Test City",
            "address": "Test Address"
        })
    )

    response = await admin_client.post("/cinemas/", json=payload.model_dump(mode="json"))

    assert response.status_code == 201

@respx.mock
async def test_get_cinema_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/cinema/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "name": "Test Cinema",
            "city": "Test City",
            "address": "Test Address"
        })
    )

    response = await admin_client.get("/cinemas/1")

    assert response.status_code == 200

@respx.mock
async def test_get_cinema_by_name(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/cinema/", params={"name": "Test Cinema"}).mock(
        return_value=Response(200, json=[{
            "id": 1,
            "name": "Test Cinema",
            "city": "Test City",
            "address": "Test Address"
        }])
    )

    response = await admin_client.get("/cinemas", params={"name": "Test Cinema"})

    assert response.status_code == 200

@respx.mock
async def test_update_cinema(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    update = UpdateCinema(
        name="Test Cinema2"
    )

    respx.patch(f"{test_settings.cinema_service_url}/cinema/1", json=update.model_dump(mode="json")).mock(
        return_value=Response(200, json={
            "id": 1,
            "name": "Test Cinema2",
            "city": "Test City",
            "address": "Test Address"
        })
    )

    response = await admin_client.patch("/cinemas/1", json=update.model_dump(mode="json"))

    assert response.status_code == 200

@respx.mock
async def test_delete_cinema_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.delete(f"{test_settings.cinema_service_url}/cinema/1").mock(
        return_value=Response(204, json={}))

    await admin_client.delete("/cinemas/1")