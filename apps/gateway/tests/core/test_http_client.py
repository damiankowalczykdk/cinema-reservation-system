import httpx
import pytest
import respx
from core.http_client import ServiceRequestClient
from fastapi import HTTPException
from httpx import ConnectError, Response


@respx.mock
async def test_connection_error() -> None:
    async with httpx.AsyncClient() as ac:
        client = ServiceRequestClient(ac, base_url="http://fake-service")

        respx.get("http://fake-service").side_effect = ConnectError("error")

        with pytest.raises(HTTPException) as exc:
            await client.request("GET", path="")

        assert exc.value.status_code == 503


@respx.mock
async def test_error_status_empty_body() -> None:
    async with httpx.AsyncClient() as ac:
        client = ServiceRequestClient(ac, base_url="http://fake-service")

        respx.get("http://fake-service").mock(return_value=Response(status_code=404))

        with pytest.raises(HTTPException) as exc:
            await client.request("GET", path="")

        assert exc.value.status_code == 404


@respx.mock
async def test_error_response_with_message_field() -> None:
    async with httpx.AsyncClient() as ac:
        client = ServiceRequestClient(ac, base_url="http://fake-service")

        respx.get("http://fake-service").mock(
            return_value=Response(status_code=404, json={"message": "not found"})
        )

        with pytest.raises(HTTPException) as exc:
            await client.request("GET", path="")

        assert exc.value.status_code == 404
        assert exc.value.detail == "not found"
