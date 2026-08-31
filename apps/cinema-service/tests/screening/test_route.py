from httpx import AsyncClient


async def  test_screening_crud_flow_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_movie = {
        "title": "Movie",
        "description": "Movie description",
        "duration_minutes": 60,
        "genre": "crime",
        "release_date": "2026-08-23",
    }

    response_movie = await client.post("/movie/", json=payload_movie)
    movie_id = response_movie.json()["id"]


    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": "2026-08-25T18:30:00Z",
        "price": 19.99
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    assert response_screening.status_code == 201

    data = response_screening.json()
    assert data["price"] == "19.99"

    response = await client.get(f"/screening/{screening_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["price"] == "19.99"


    update_screening = {
        "price": 29.99
    }
    response_update = await client.patch(f"/screening/{screening_id}", json=update_screening)
    data = response_update.json()
    assert response_update.status_code == 200

    assert data["price"] == "29.99"

    response_delete = await client.delete(f"/screening/{screening_id}")

    assert response_delete.status_code == 204

    response = await client.get(f"/screening/{screening_id}")


    assert response.status_code == 404
