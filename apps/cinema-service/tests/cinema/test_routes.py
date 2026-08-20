from httpx import AsyncClient
from domain.models.cinema import Cinema


async def test_create_cinema_success(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response = await client.post("/cinema/", json=payload)
    assert response.status_code == 201

async def test_create_cinema_failed(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    await client.post("/cinema/", json=payload)

    response = await client.post("/cinema/", json=payload)
    assert response.status_code == 409

async def test_get_cinema_by_id_success(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response = await client.post("/cinema/", json=payload)
    cinema_id = response.json()["id"]

    result = await client.get(f"/cinema/{cinema_id}")
    assert result.status_code == 200

    data = result.json()
    assert data["name"] == "Test Cinema"
    assert data["city"] == "Test City"

async def test_get_cinema_by_id_not_found(client: AsyncClient) -> None:

    result = await client.get(f"/cinema/1")
    assert result.status_code == 404


async def test_get_cinema_by_name_success(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response = await client.post("/cinema/", json=payload)
    cinema_name = response.json()["name"]

    result = await client.get(f"/cinema/?name={cinema_name}")
    assert result.status_code == 200

    data = result.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Cinema"
    assert data[0]["city"] == "Test City"


def test_cinema_repr() -> None:
    cinema = Cinema(id=4, name="Test Cinema", city="Test City", address="Test Address")

    assert repr(cinema) == "<Cinema: Test Cinema city: Test City address: Test Address >"

async def test_get_cinema_by_name_not_found(client: AsyncClient) -> None:

    result = await client.get(f"/cinema/?name=test")
    assert result.status_code == 404

async def test_update_cinema_success(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response = await client.post("/cinema/", json=payload)
    cinema_id = response.json()["id"]

    updated_payload = {
        "name": "Test Cinema2",
        "city": "Test City2",
        "address": "Test Address2"
    }
    await client.patch(f"/cinema/{cinema_id}", json=updated_payload)

    result = await client.get(f"/cinema/{cinema_id}")
    assert result.status_code == 200

    data = result.json()
    assert data["name"] == "Test Cinema2"
    assert data["city"] == "Test City2"


async def test_delete_cinema_by_id_success(client: AsyncClient) -> None:
    payload = {
        "name": "Test Cinema",
        "city": "Test City",
        "address": "Test Address"
    }
    response = await client.post("/cinema/", json=payload)
    cinema_id = response.json()["id"]

    cinema = await client.get(f"/cinema/{cinema_id}")
    assert cinema.status_code == 200

    del_cinema = await client.delete(f"/cinema/{cinema_id}")
    assert del_cinema.status_code == 204

    not_found_cinema = await client.get(f"/cinema/{cinema_id}")
    assert not_found_cinema.status_code == 404

async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "cinema-service"


