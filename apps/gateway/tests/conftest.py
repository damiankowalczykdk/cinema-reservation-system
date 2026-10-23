from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from core.config import Auth0Settings, get_settings
from core.security import get_current_user
from domain.schemas.auth import TokenPayload
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture(scope="session")
def test_settings() -> Auth0Settings:
    return Auth0Settings(
        cinema_service_url="http://mock-cinema-service",
        payment_service_url="http://mock-payment-service",
        ai_service_url="http://mock-ai-service",
        http_timeout=5,
    )  # type: ignore


@pytest_asyncio.fixture
async def client(test_settings: Auth0Settings) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(
    test_settings: Auth0Settings,
) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: TokenPayload(
        sub="test123", roles=["admin"]
    )  # type: ignore
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_client(
    test_settings: Auth0Settings,
) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: TokenPayload(
        sub="test123user", roles=["user"], email="test@example.com"
    )  # type: ignore
    app.state.http_client = httpx.AsyncClient()

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
