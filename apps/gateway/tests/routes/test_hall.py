import respx
from httpx import AsyncClient, Response
from core.config import Auth0Settings
from domain.schemas.hall import CreateHall, UpdateHall
from tests.conftest import admin_client


@respx.mock
async def test_create_hall(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateHall(
        cinema_id=1,
        name="Hall 1",
        rows=10,
        seats_per_row=10
    )

    respx.post(f"{test_settings.cinema_service_url}/hall/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "cinema_id": 1,
            "name": "Hall 1",
            "rows": 10,
            "seats_per_row": 10
        })
      )

    response = await admin_client.post( "/halls/", json=payload.model_dump(mode="json"))

    assert response.status_code == 201

@respx.mock
async def test_get_hall_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/hall/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "cinema_id": 1,
            "name": "Hall 1",
            "rows": 10,
            "seats_per_row": 10
        })
    )

    response = await admin_client.get("/halls/1")

    assert response.status_code == 200

@respx.mock
async def test_get_hall_by_name(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/hall/", params={"cinema_id": 1, "name": "Hall 1"}).mock(
        return_value=Response(200, json={
            "id": 1,
            "cinema_id": 1,
            "name": "Hall 1",
            "rows": 10,
            "seats_per_row": 10
        })
    )

    response = await admin_client.get("/halls", params={"cinema_id": 1, "name": "Hall 1"})
    data = response.json()

    assert response.status_code == 200
    assert data["rows"] == 10

@respx.mock
async def test_update_hall(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = UpdateHall(
        name="Hall 2",
    )
    respx.patch(f"{test_settings.cinema_service_url}/hall/1", json=payload.model_dump(mode="json")).mock(
        return_value=Response(200, json={
             "id": 1,
            "cinema_id": 1,
            "name": "Hall 2",
            "rows": 10,
            "seats_per_row": 10
    }))

    response = await admin_client.patch("/halls/1", json=payload.model_dump(mode="json"))
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Hall 2"

@respx.mock
async def test_delete_cinema_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.delete(f"{test_settings.cinema_service_url}/hall/1").mock(
        return_value=Response(204, json={}))

    await admin_client.delete("/halls/1")