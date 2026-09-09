import respx
from httpx import AsyncClient, Response

from core.config import Auth0Settings
from domain.schemas.reservation import CreateReservation, Status


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