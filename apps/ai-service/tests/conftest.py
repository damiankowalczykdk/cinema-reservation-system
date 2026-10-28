from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from api.dependencies import get_conversation_repository, get_settings
from core.config import Settings
from httpx import ASGITransport, AsyncClient
from main import app
from openai import AsyncOpenAI


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        cinema_service_url="http://mock-cinema-service",
        openai_api_key="mock-openai_api_key",
    )  # type: ignore


@pytest.fixture
def conversation_repository() -> AsyncMock:
    mock = AsyncMock()
    mock.get.return_value = None
    return mock


@pytest_asyncio.fixture
async def client(
    test_settings: Settings, conversation_repository: AsyncMock
) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_conversation_repository] = lambda: (
        conversation_repository
    )
    app.state.http_client = httpx.AsyncClient()
    app.state.openai_client = AsyncOpenAI(api_key=test_settings.openai_api_key)

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def fake_cinema_client():
    mock = AsyncMock()
    mock.request.return_value = [
        {
            "screening_id": 1,
            "movie_title": "Test Movie Title",
            "cinema_name": "Test Cinema Name",
            "city": "Test City",
            "genre": "animation",
            "start_time": datetime.now(UTC).isoformat(),
            "price": 100,
        }
    ]

    return mock


@pytest.fixture
def fake_cinema_client_reservation_read():
    mock = AsyncMock()
    mock.request.return_value = [
        {
            "group_id": 1,
            "screening_id": 1,
            "guest_email": "test@example.com",
            "row": 1,
            "seat": 1,
            "status": "paiding",
            "price_paid": Decimal(100),
            "expires_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
        }
    ]
    return mock


@pytest.fixture
def fake_cinema_client_seat_map():
    mock = AsyncMock()
    mock.request.return_value = {
        "seats": [[1, 1]],
        "row": 1,
        "seat_per_row": 1,
    }
    return mock
