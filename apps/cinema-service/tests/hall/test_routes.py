from httpx import AsyncClient


async def test_create_hall_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response = await client.post("/hall/", json=payload_hall)
    data = response.json()

    assert response.status_code == 201
    assert data["cinema_id"] == cinema_id
    assert data["name"] == "Test Hall"


async def test_get_hall_by_id_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]


    result = await client.get(f"/hall/{hall_id}")

    data = result.json()
    assert result.status_code == 200

    assert data["name"] == "Test Hall"
    assert data["rows"] == 10
    assert data["seats_per_row"] == 10


async def test_get_hall_by_name_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_name = response_hall.json()["name"]

    result = await client.get(f"/hall/", params={"cinema_id": cinema_id, "name": hall_name})

    data = result.json()
    assert result.status_code == 200

    assert data["name"] == "Test Hall"
    assert data["rows"] == 10
    assert data["seats_per_row"] == 10

async def test_update_hall_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    updated_hall = {
        "name": "Test Hall New Name",
        "rows": 10,
        "seats_per_row": 10
    }

    response = await client.patch(f"/hall/{hall_id}", json=updated_hall)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Hall New Name"

async def test_delete_hall_by_id_success(client: AsyncClient) -> None:
    payload_cinema = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response_cinema = await client.post("/cinema/", json=payload_cinema)

    cinema_id = response_cinema.json()["id"]

    payload_hall = {
        "cinema_id": cinema_id,
        "name": "Test Hall",
        "rows": 10,
        "seats_per_row": 10
    }
    response_hall = await client.post("/hall/", json=payload_hall)
    hall_id = response_hall.json()["id"]

    response = await client.delete(f"/hall/{hall_id}")
    assert response.status_code == 204