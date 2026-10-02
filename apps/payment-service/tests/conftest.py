from typing import AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
import stripe
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from testcontainers.community.postgres import PostgresContainer

from api.dependencies import get_stripe_client, get_cinema_client
from core.database import Base, get_db
from main import app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as container:
        yield container


@pytest_asyncio.fixture(scope="session")
async def engine(postgres_container) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(postgres_container.get_connection_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def fake_stripe_client():
    mock = MagicMock()
    mock.v1.checkout.sessions.create.return_value = MagicMock(
        id="cs_123",
        url="https://checkout.stripe.com/test",
        expires_at=datetime.now(timezone.utc)
    )
    mock.v1.checkout.sessions.retrieve.return_value = MagicMock(
        status="open",
        url="https://checkout.stripe.com/test",
        payment_intent="pi_123",
        expires_at=datetime.now(timezone.utc)
    )
    return mock

@pytest.fixture
def fake_stripe_client_stripe_error():
    mock = MagicMock()
    mock.v1.checkout.sessions.create.side_effect = stripe.StripeError()
    mock.v1.checkout.sessions.retrieve.side_effect = stripe.StripeError()
    return mock

@pytest.fixture
def fake_stripe_client_provider_error():
    mock = MagicMock()
    mock.v1.checkout.sessions.create.return_value = MagicMock(
        id="cs_123",
        url="https://checkout.stripe.com/test"
    )
    mock.v1.checkout.sessions.retrieve.return_value = MagicMock(
        status="open",
        url="https://checkout.stripe.com/test",
        payment_intent=123
    )
    return mock

@pytest.fixture
def fake_stripe_client_expired():
    mock = MagicMock()
    mock.v1.checkout.sessions.create.return_value = MagicMock(
        id="cs_123",
        url="https://checkout.stripe.com/test"
    )
    mock.v1.checkout.sessions.retrieve.return_value = MagicMock(
        status="expired",
        url="https://checkout.stripe.com/test",
        payment_intent="pi_123",

    )
    return mock

@pytest_asyncio.fixture
async def fake_cinema_client():
    mock = AsyncMock()
    mock.request.return_value = {
        "total_price":"100",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=60)).isoformat()
    }
    return mock

@pytest_asyncio.fixture
async def fake_cinema_client_expire_time():
    mock = AsyncMock()
    mock.request.return_value = {
        "total_price":"100",
        "expires_at": (datetime.now(timezone.utc) - timedelta(minutes=60)).isoformat()
    }
    return mock

@pytest_asyncio.fixture
async def fake_cinema_client_conflict():
    mock = AsyncMock()
    mock.request.side_effect = HTTPException(status_code=409)
    return mock

@pytest_asyncio.fixture
async def fake_cinema_client_unavailable():
    mock = AsyncMock()
    mock.request.side_effect = HTTPException(status_code=503)
    return mock

@pytest_asyncio.fixture
async def client(db_session, fake_cinema_client, fake_stripe_client):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db


    app.dependency_overrides[get_stripe_client] = lambda: fake_stripe_client
    app.dependency_overrides[get_cinema_client] = lambda: fake_cinema_client


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()



