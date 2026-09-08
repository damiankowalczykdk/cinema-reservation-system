from datetime import datetime
from decimal import Decimal

import respx
from httpx import AsyncClient, Response

from core.config import Auth0Settings
from domain.schemas.screening import CreateScreening, UpdateScreening
from tests.conftest import admin_client, user_client


@respx.mock
async def test_create_screening(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateScreening(
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 9, 6, 18,0,0),
        price=Decimal("10.00"),
    )

    respx.post(f"{test_settings.cinema_service_url}/screening/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 10.00
        })
    )

    response = await client.post(f"/screenings/", json=payload.model_dump(mode="json"))
    data = response.json()
    assert response.status_code == 201
    assert data["movie_id"] == 1

@respx.mock
async def test_create_screening_validation_exception(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateScreening(
        movie_id=1,
        hall_id=1,
        start_time=datetime(2026, 9, 6, 18,0,0),
        price=Decimal("10.00"),
    )

    respx.post(f"{test_settings.cinema_service_url}/screening/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 10.00
        })
    )

    response = await admin_client.post(f"/screenings/", json={
        "movie_id": 1,
        "hall_id": 1,
        "start_time": "2026-09-06T18:00:00Z"
    })

    assert response.status_code == 422


@respx.mock
async def test_get_screening_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/screening/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 10.00
        })
    )

    response = await admin_client.get(f"/screenings/1")
    data = response.json()
    assert response.status_code == 200
    assert data["movie_id"] == 1


@respx.mock
async def test_get_screening_by_id_unauthorized(client: AsyncClient,  test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/screening/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 10.00
        })
    )

    response = await client.get(f"/screenings/1")

    assert response.status_code == 401

@respx.mock
async def test_get_screening_by_id_forbidden_roles(client: AsyncClient, user_client: AsyncClient,  test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/screening/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 10.00
        })
    )

    response = await user_client.get(f"/screenings/1")

    assert response.status_code == 403

@respx.mock
async def test_update_screening(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = UpdateScreening(
        price=Decimal("100.00")
    )

    respx.patch(f"{test_settings.cinema_service_url}/screening/1", json=payload.model_dump(mode="json")).mock(
        return_value=Response(200, json={
            "id": 1,
            "movie_id": 1,
            "hall_id": 1,
            "start_time": "2026-09-06T18:00:00Z",
            "price": 100.00
        })
    )

    response = await client.patch(f"/screenings/1", json=payload.model_dump(mode="json"))
    assert response.status_code == 200

    data = response.json()
    assert data["price"] == "100.0"


@respx.mock
async def test_delete_screening_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.delete(f"{test_settings.cinema_service_url}/screening/1").mock(
        return_value=Response(204, json={}))

    response = await client.delete(f"/screenings/1")

    assert response.status_code == 204
