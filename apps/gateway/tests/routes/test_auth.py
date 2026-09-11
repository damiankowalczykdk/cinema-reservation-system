import urllib
from http.client import HTTPException

import pytest
import respx
from httpx import AsyncClient, Response
from core.config import settings


async def test_get_login_url(client: AsyncClient) -> None:

    response = await client.get("/auth/login-url")

    assert response.status_code == 200

    data = response.json()
    assert "url" in data

    url = data["url"]

    parse = urllib.parse.urlparse(url)

    assert parse.scheme == "https"

async def test_get_current_user(user_client: AsyncClient) -> None:

    response = await user_client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()

    assert data["sub"] == "test123user"



async def test_logout(user_client: AsyncClient) -> None:

    response = await user_client.post("/auth/logout")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Successfully logged out."

async def test_logout_url(client: AsyncClient) -> None:
    response = await client.get("/auth/logout-url")

    assert response.status_code == 200
    data = response.json()

    url = data["url"]

    parse = urllib.parse.urlparse(url)

    assert parse.path == "/v2/logout"

@respx.mock
async def test_callback(client: AsyncClient) -> None:
    response = await client.get("/auth/login-url")

    data = response.json()


    url = data["url"]

    query = urllib.parse.parse_qs(url)


    state = query["state"][0]

    respx.post(f"https://{settings.auth0_domain}/oauth/token").mock(
        return_value=Response(200, json={"access_token": "fake-token", "expires_in": 3600}))

    response = await client.get("/auth/callback", params={"code": "fake-code", "state": state})

    assert response.status_code == 307
    assert response.headers["Location"] == settings.app_base_url


async def test_callback_invalid_state(client: AsyncClient) -> None:

    response =  await client.get("/auth/callback", params={"code": "fake-code", "state": "bad-state"})

    assert response.status_code == 400


async def test_callback_invalid_authorization_code(client: AsyncClient) -> None:
    response = await client.get("/auth/login-url")

    data = response.json()

    url = data["url"]

    query = urllib.parse.parse_qs(url)

    state = query["state"][0]

    response =  await client.get("/auth/callback", params={"code": "bad-code", "state": state})

    assert response.status_code == 502


