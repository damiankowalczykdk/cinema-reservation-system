from unittest.mock import MagicMock

import pytest

from service.assistant import AssistantService


@pytest.fixture
def assistant_service(fake_cinema_client: MagicMock) -> AssistantService:
    return AssistantService(cinema_client=fake_cinema_client)


async def test_search_showtimes(assistant_service: AssistantService) -> None:

    result = await assistant_service.search_showtimes(city="Test City", genre=None, after=None, before=None)

    assert result is not None

    assert result[0].price == 100