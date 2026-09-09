import respx
from httpx import AsyncClient, Response

from core.config import Auth0Settings
from domain.schemas.reservation import CreateReservation


@respx.mock
async def test_create_reservation(client: AsyncClient, user_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateReservation(
        screening_id=1,
        row=1,
        seat=1
    )

    respx.post(f"{test_settings.cinema_service_url}/reservation/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "screening_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        })
    )

    response = await user_client.post("/reservations/", json=payload.model_dump(mode="json"))
    assert response.status_code == 201

    data = response.json()
    assert data["screening_id"] == 1


@respx.mock
async def test_get_reservation_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:

    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "screening_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        })
    )

    response = await admin_client.get("/reservations/1")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test123user"

@respx.mock
async def test_get_user_reservations(client: AsyncClient, user_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/reservation/").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        }])
    )

    response = await user_client.get("/reservations/")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["user_id"] == "test123user"

@respx.mock
async def test_cancel_reservation(client: AsyncClient, user_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.post(f"{test_settings.cinema_service_url}/reservation/1/cancel").mock(
        return_value=Response(200, json={
            "id": 1,
            "screening_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        })
    )

    response = await user_client.post("/reservations/1/cancel")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test123user"

@respx.mock
async def test_get_occupied_seats(client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/reservation/screening/1/seats").mock(
        return_value=Response(200, json={
            "seats": [[1,1]],
            "row": 1,
            "seat_per_row": 1
        }))

    response = await client.get("/reservations/screening/1/seats")
    assert response.status_code == 200

@respx.mock
async def test_delete_reservation_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.delete(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(204, json={})
    )

    response = await admin_client.delete("/reservations/1")
    assert response.status_code == 204



