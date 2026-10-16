import httpx2
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from openai import APIStatusError, APIConnectionError, APITimeoutError


async def test_unhandled_exception_handler(client: AsyncClient) -> None:

    with patch("api.routes.assistant.run_agent",new_callable= AsyncMock, side_effect=Exception("boom")):
        response = await client.post(
            "/assistant",
            json={"message": "Test message"})

        assert response.status_code == 500
        assert response.json()["error"] == "INTERNAL_SERVER_ERROR"

async def test_validation_exception_handler(client: AsyncClient) -> None:

    with patch("api.routes.assistant.run_agent",new_callable= AsyncMock, side_effect=Exception("boom")):
        response = await client.post(
            "/assistant",
            json={"bad_field": 1})

        assert response.status_code == 422
        assert response.json()["error"] == "VALIDATION_ERROR"

async def test_handler_api_status_error(client: AsyncClient) -> None:

    with patch(
            "api.routes.assistant.run_agent",
            new_callable= AsyncMock,
            side_effect=APIStatusError(
                "error",
                response=httpx2.Response(status_code=502, request=httpx2.Request("POST", "http://test")), body=None)):

        response = await client.post(
            "/assistant",
            json={"message": "Test message"})

        assert response.status_code == 502
        assert response.json()["error"] == "LLM_ERROR"


async def test_handler_api_connection_error(client: AsyncClient) -> None:

    with patch(
            "api.routes.assistant.run_agent",
            new_callable= AsyncMock,
            side_effect= APIConnectionError(
                request=httpx2.Request("POST", "http://test"))):

        response = await client.post(
            "/assistant",
            json={"message": "Test message"})

        assert response.status_code == 503
        assert response.json()["error"] == "LLM_UNAVAILABLE"


async def test_handler_api_timeout_error(client: AsyncClient) -> None:

    with patch(
            "api.routes.assistant.run_agent",
            new_callable= AsyncMock,
            side_effect= APITimeoutError(
                request=httpx2.Request("POST", "http://test"))):

        response = await client.post(
            "/assistant",
            json={"message": "Test message"})

        assert response.status_code == 504
        assert response.json()["error"] == "LLM_TIMEOUT"