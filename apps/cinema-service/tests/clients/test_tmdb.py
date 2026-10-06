from http.client import responses
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from clients.tmdb import TMDBClient


@pytest.fixture
def mock_client():
    return AsyncMock(spec=httpx.AsyncClient)

@pytest.fixture
def mock_tmdb_api_token() -> str:
    return "test_token"

@pytest.fixture
def mock_tmdb_base_address() -> str:
    return "test_base_address"

@pytest.fixture
def tmdb_client(mock_client, mock_tmdb_api_token: str, mock_tmdb_base_address: str) -> TMDBClient:
    return TMDBClient(
        client=mock_client,
        tmdb_api_token=mock_tmdb_api_token,
        tmdb_base_address=mock_tmdb_base_address
    )


async def test_get_poster_path_request_error(tmdb_client: TMDBClient, mock_client: AsyncMock) -> None:
    mock_client.request.side_effect = httpx.ConnectError("boom")

    await tmdb_client.get_poster_path("test", 2026)


async def test_get_poster_path_status_code_404(tmdb_client: TMDBClient, mock_client: AsyncMock) -> None:
    mock_client.request.return_value = httpx.Response(status_code=404)

    await tmdb_client.get_poster_path("test", 2026)

async def test_get_poster_path_list_empty(tmdb_client: TMDBClient, mock_client: AsyncMock) -> None:
    mock_client.request.return_value = httpx.Response(status_code=200, json={"results": []})

    await tmdb_client.get_poster_path("test", 2026)




