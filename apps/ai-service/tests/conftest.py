from decimal import Decimal
from typing import AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
import httpx
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from api.dependencies import get_settings
from main import app
from core.config import Settings
import pytest

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        cinema_service_url="http://mock-cinema-service"
    ) #type: ignore

@pytest_asyncio.fixture
async def client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(transport=ASGITransport(app=app,  raise_app_exceptions=False), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
def fake_cinema_client():
    mock = AsyncMock()
    mock.request.return_value = [{
        "screening_id": 1,
        "movie_title": "Test Movie Title",
        "cinema_name": "Test Cinema Name",
        "city": "Test City",
        "genre": "animation",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "price": 100
    }]

    return mock
