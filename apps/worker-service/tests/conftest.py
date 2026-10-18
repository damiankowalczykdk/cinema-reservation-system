from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from temporalio.testing import WorkflowEnvironment

from activities import ReservationActivities


@pytest.fixture
async def mock_temporal_client() -> AsyncMock:
    mock = AsyncMock()
    mock.request = AsyncMock(return_value=MagicMock())
    return mock

@pytest.fixture
async def mock_reservation_activities(mock_temporal_client: AsyncMock) -> ReservationActivities:
    return ReservationActivities(mock_temporal_client)

@pytest_asyncio.fixture(scope="session")
async def workflow_testing() -> AsyncIterator[WorkflowEnvironment]:
    async with await WorkflowEnvironment.start_time_skipping() as workflow_test:
        yield workflow_test


