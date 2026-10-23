from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def test_create_reservation(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    _ = await client.post("/screening/", json=payload_screening)

    payload = {
        "screening_id": 1,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
        "currency": "pln",
    }

    response = await client.post("/reservation/", json=payload)

    data = response.json()[0]

    assert response.status_code == 201

    assert data["screening_id"] == 1
    assert data["row"] == 1
    assert data["seat"] == 1
    assert data["guest_email"] == "example@example.com"


async def test_get_reservation_summary(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
        "currency": "pln",
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.get(f"/reservation/{group_id}/summary")

    data = response.json()

    assert data["group_id"] == group_id
    assert data["city"] == "Test City"
    assert data["total_price"] == "19.99"


async def test_get_reservation_by_group_id(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
        "currency": "pln",
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.get(f"/reservation/{group_id}")
    data = response.json()[0]

    assert response.status_code == 200

    assert data["row"] == 1


async def test_get_group_total(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.get(f"/reservation/{group_id}/total")
    data = response.json()

    assert response.status_code == 200

    assert data["total_price"] == "19.99"


async def test_get_user_reservations_and_cancel_reservation(
    client: AsyncClient,
) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {"screening_id": screening_id, "seats": [{"row": 1, "seat": 1}]}

    _ = await client.post(
        "/reservation/", json=payload, headers={"X-User-Id": "test-user123"}
    )

    response = await client.get("/reservation/", headers={"X-User-Id": "test-user123"})
    data = response.json()

    assert response.status_code == 200

    assert data[0]["screening_id"] == screening_id
    assert data[0]["row"] == 1

    group_id = response.json()[0]["group_id"]

    cancel_reservation = await client.post(
        f"/reservation/{group_id}/cancel", headers={"X-User-Id": "test-user123"}
    )

    assert cancel_reservation.status_code == 200


async def test_get_occupied_seats(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {"screening_id": screening_id, "seats": [{"row": 1, "seat": 1}]}

    response_reservation = await client.post(
        "/reservation/", json=payload, headers={"X-User-Id": "test-user123"}
    )

    _ = await client.get("/reservation/", headers={"X-User-Id": "test-user123"})

    response = await client.get(f"/reservation/screening/{screening_id}/seats")
    data = response.json()

    assert response_reservation.status_code == 201

    assert data["seats"] == [[1, 1]]


async def test_delete_reservation_by_id(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.delete(f"/reservation/{group_id}")

    assert response.status_code == 204


async def test_set_confirm_reservation(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.post(f"/reservation/{group_id}/confirm")
    assert response.status_code == 200

    get_reservation = await client.get(f"/reservation/{group_id}")
    data = get_reservation.json()

    assert data[0]["status"] == "confirmed"


async def test_extend(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    get_reservation = await client.get(f"/reservation/{group_id}")
    data = get_reservation.json()

    assert data[0]["status"] == "pending"

    extend_response = await client.post(f"/reservation/{group_id}/extend")

    assert extend_response.status_code == 200

    data_extend = extend_response.json()

    assert "expires_at" in data_extend


async def test_expire_group(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    response = await client.post(f"/reservation/{group_id}/expire")

    assert response.status_code == 200


async def test_verify_ticket(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address",
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
        "seats_per_row": 10,
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    payload_screening = {
        "movie_id": movie_id,
        "hall_id": hall_id,
        "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "price": 19.99,
        "currency": "pln",
    }

    response_screening = await client.post("/screening/", json=payload_screening)
    screening_id = response_screening.json()["id"]

    payload = {
        "screening_id": screening_id,
        "seats": [{"row": 1, "seat": 1}],
        "guest_email": "example@example.com",
    }

    response_reservation = await client.post("/reservation/", json=payload)

    group_id = response_reservation.json()[0]["group_id"]

    await client.post(f"/reservation/{group_id}/confirm")

    response_summary = await client.get(f"/reservation/{group_id}/summary")

    ticket_code = response_summary.json()["ticket_code"]

    payload = {"ticket_code": ticket_code}

    response = await client.post("/reservation/ticket/verify", json=payload)

    data = response.json()
    assert response.status_code == 200

    assert data["ticket_code"] == ticket_code
