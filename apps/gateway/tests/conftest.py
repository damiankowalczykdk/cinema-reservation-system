from typing import AsyncGenerator

import httpx
import pytest_asyncio
from fastapi_cloud_cli.config import Settings
from httpx import AsyncClient, ASGITransport

from core.security import get_current_user
from core.config import get_settings, Auth0Settings
from domain.schemas.auth import TokenPayload
from main import app
import pytest

@pytest.fixture(scope="session")
def test_settings() -> Auth0Settings:
    return Auth0Settings(
        cinema_service_url="http://mock-cinema-service",
        http_timeout=5
    ) #type: ignore

@pytest_asyncio.fixture
async def client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(transport=ASGITransport(app=app,  raise_app_exceptions=False), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_current_user] = lambda: TokenPayload(sub="test123", roles=["admin"]) # type: ignore
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(transport=ASGITransport(app=app,  raise_app_exceptions=False), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def user_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_current_user] = lambda: TokenPayload(sub="test123user", roles=["user"]) # type: ignore
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(transport=ASGITransport(app=app,  raise_app_exceptions=False), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()