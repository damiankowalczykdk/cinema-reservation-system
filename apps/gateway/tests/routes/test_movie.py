from datetime import date

import respx
from httpx import AsyncClient, Response
from core.config import Auth0Settings
from domain.schemas.movie import CreateMovie, Genre, UpdateMovie
from tests.conftest import admin_client


@respx.mock
async def test_create_movie(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    payload = CreateMovie(
        title="Movie Title",
        description="Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,9,5)
    )

    respx.post(f"{test_settings.cinema_service_url}/movie/", json=payload.model_dump(mode="json")).mock(
        return_value=Response(201, json={
            "id": 1,
            "title": "Movie Title",
            "description": "Movie Description",
            "duration_minutes": 60,
            "genre": "crime",
            "release_date": "2026-09-05"
        })
    )

    response = await admin_client.post("/movies/", json=payload.model_dump(mode="json"))
    data = response.json()

    assert response.status_code == 201

    assert data["genre"] == "crime"

@respx.mock
async def test_get_movie_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:

    respx.get(f"{test_settings.cinema_service_url}/movie/1").mock(
        return_value=Response(200, json={
            "id": 1,
            "title": "Movie Title",
            "description": "Movie Description",
            "duration_minutes": 60,
            "genre": "crime",
            "release_date": "2026-09-05"
        })
    )

    response = await admin_client.get("/movies/1")
    data = response.json()
    assert response.status_code == 200

    assert data["title"] == "Movie Title"

@respx.mock
async def test_get_movie_by_title(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.get(f"{test_settings.cinema_service_url}/movie/", params={"title": "Movie Title"}).mock(
        return_value=Response(200, json=[{
            "id": 1,
            "title": "Movie Title",
            "description": "Movie Description",
            "duration_minutes": 60,
            "genre": "crime",
            "release_date": "2026-09-05"
        }])
    )

    response = await admin_client.get("/movies", params={"title": "Movie Title"})

    data = response.json()
    assert response.status_code == 200

    assert data[0]["title"] == "Movie Title"


@respx.mock
async def test_update_movie(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:

    payload = UpdateMovie(
        title="Movie Title2"
    )

    respx.patch(f"{test_settings.cinema_service_url}/movie/1", json=payload.model_dump(mode="json")).mock(
        return_value=Response(200, json={
            "id": 1,
            "title": "Movie Title2",
            "description": "Movie Description",
            "duration_minutes": 60,
            "genre": "crime",
            "release_date": "2026-09-05"
        })
    )

    response = await admin_client.patch("/movies/1", json=payload.model_dump(mode="json"))
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "Movie Title2"


@respx.mock
async def test_delete_movie_by_id(client: AsyncClient, admin_client: AsyncClient, test_settings: Auth0Settings) -> None:
    respx.delete(f"{test_settings.cinema_service_url}/movie/1").mock(
        return_value=Response(204, json={})
    )

    response = await admin_client.delete("/movies/1")

    assert response.status_code == 204