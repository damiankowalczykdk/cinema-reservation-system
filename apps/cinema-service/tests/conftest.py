from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from testcontainers.community.postgres import PostgresContainer

from api.dependencies import get_temporal_client
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
def mock_temporal_client() -> AsyncMock:
    mock = AsyncMock()
    mock.get_workflow_handle = MagicMock(return_value=AsyncMock())
    return mock

@pytest_asyncio.fixture
async def client(db_session, mock_temporal_client):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_temporal_client] = lambda: mock_temporal_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_tmdb_client() -> AsyncMock:
    mock = AsyncMock()
    mock.get_poster_path.return_value = ("test.jpg", 1)
    mock.get_trailer_key.return_value = "test_key"

    return mock

