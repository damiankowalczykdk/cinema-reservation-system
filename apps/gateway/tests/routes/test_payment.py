from http.client import responses

import respx
from httpx import AsyncClient, Response

from core.config import Auth0Settings
from domain.schemas.payment import CreatePayment



@respx.mock
async def test_create_payment(client: AsyncClient, user_client:AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreatePayment(
        group_id=1
    )
    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "group_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        }])
    )

    respx.post(f"{test_settings.payment_service_url}/payment", json=payload.model_dump(mode="json")).mock(
        return_value=Response(status_code=201, json={"checkout_url": "https://checkout.stripe.com/test"})
    )

    response = await user_client.post("/payments", json=payload.model_dump(mode="json"))

    assert response.status_code == 201

@respx.mock
async def test_create_payment_anonymous_for_user_reservation_forbidden(client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreatePayment(
        group_id=1
    )
    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "group_id": 1,
            "user_id": "test123user",
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        }])
    )

    respx.post(f"{test_settings.payment_service_url}/payment", json=payload.model_dump(mode="json")).mock(
        return_value=Response(status_code=201, json={"checkout_url": "https://checkout.stripe.com/test"})
    )

    response = await client.post("/payments", json=payload.model_dump(mode="json"))

    assert response.status_code == 403


@respx.mock
async def  test_create_payment_guest_without_email_forbidden(client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreatePayment(
        group_id=1
    )
    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "group_id": 1,
            "user_id": None,
            "guest_email": None,
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        }])
    )

    respx.post(f"{test_settings.payment_service_url}/payment", json=payload.model_dump(mode="json")).mock(
        return_value=Response(status_code=201, json={"checkout_url": "https://checkout.stripe.com/test"})
    )

    response = await client.post("/payments", json=payload.model_dump(mode="json"))

    assert response.status_code == 403

@respx.mock
async def  test_create_payment_guest_email_mismatch_forbidden(client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreatePayment(
        group_id=1,
        guest_email="test@user.com",

    )
    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "group_id": 1,
            "user_id": None,
            "guest_email": "bad_email",
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "pending",
            "price_paid": 100
        }])
    )

    respx.post(f"{test_settings.payment_service_url}/payment", json=payload.model_dump(mode="json")).mock(
        return_value=Response(status_code=201, json={"checkout_url": "https://checkout.stripe.com/test"})
    )

    response = await client.post("/payments", json=payload.model_dump(mode="json"))

    assert response.status_code == 403

@respx.mock
async def test_create_payment_reservation_not_pending(client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreatePayment(
        group_id=1,
        guest_email="test@user.com"

    )
    respx.get(f"{test_settings.cinema_service_url}/reservation/1").mock(
        return_value=Response(200, json=[{
            "id": 1,
            "screening_id": 1,
            "group_id": 1,
            "user_id": None,
            "guest_email": "test@user.com",
            "guest_name": None,
            "row": 1,
            "seat": 1,
            "status": "cancelled",
            "price_paid": 100
        }])
    )

    respx.post(f"{test_settings.payment_service_url}/payment", json=payload.model_dump(mode="json")).mock(
        return_value=Response(status_code=201, json={"checkout_url": "https://checkout.stripe.com/test"})
    )

    response = await client.post("/payments", json=payload.model_dump(mode="json"))

    data = response.json()

    assert response.status_code == 404

    assert data["detail"] == "Reservation is not pending"