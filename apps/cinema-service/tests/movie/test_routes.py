import datetime

from httpx import AsyncClient

from domain.schemas.movie import UpdateMovie


async def test_create_movie_success(client: AsyncClient) -> None:
    payload = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response = await client.post("/movie/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 1
    assert data["title"] == "Movie"

async def test_get_movie_by_id_success(client: AsyncClient) -> None:
    payload = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response_movie = await client.post("/movie/", json=payload)
    cinema_id = response_movie.json()["id"]

    response = await client.get(f"/movie/{cinema_id}")
    data = response.json()

    assert response.status_code == 200

    assert data["title"] == "Movie"
    assert data["release_date"] == "2026-08-23"


async def test_get_movie_by_title_success(client: AsyncClient) -> None:
    payload = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response_movie = await client.post("/movie/", json=payload)
    cinema_title = response_movie.json()["title"]

    response = await client.get(f"/movie/", params={"title": cinema_title})

    assert response.status_code == 200

    data = response.json()[0]
    assert data["description"] == "Movie description"

async def test_update_movie_success(client: AsyncClient) -> None:
    payload = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response_movie = await client.post("/movie/", json=payload)
    movie_id = response_movie.json()["id"]

    update_movie = {
        "description": "NEW Movie description"
    }

    await client.patch(f"/movie/{movie_id}", json=update_movie)

    response = await client.get(f"/movie/{movie_id}")
    data = response.json()
    assert response.status_code == 200

    assert data["description"] == "NEW Movie description"


async def test_delete_movie_success(client: AsyncClient) -> None:
    payload = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response_movie = await client.post("/movie/", json=payload)
    movie_id = response_movie.json()["id"]

    response = await client.delete(f"/movie/{movie_id}")

    assert response.status_code == 204


