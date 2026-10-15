from unittest.mock import AsyncMock
import json
import pytest


from core.config import settings
from repository.conversation import ConversationRepository


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def conversation_repository(mock_redis_client: AsyncMock) -> ConversationRepository:
    return ConversationRepository(mock_redis_client)

async def test_get_returns_none_when_conversation_not_found(
        conversation_repository: ConversationRepository,
        mock_redis_client: AsyncMock
) -> None:

    mock_redis_client.get.return_value = None

    res = await conversation_repository.get("conversation1", "user1")

    assert res is None

    mock_redis_client.get.assert_awaited_with("conversation:conversation1")

async def test_get_returns_none_when_user_id_mismatch(
        conversation_repository: ConversationRepository,
        mock_redis_client: AsyncMock
) -> None:
    mock_redis_client.get.return_value = json.dumps({"user_id": "user1", "items": [{"role":"user", "content": "Hello"}]})

    res = await conversation_repository.get("conversation2", "bad_user")

    assert res is None

    mock_redis_client.get.assert_awaited_with("conversation:conversation2")


async def test_get_returns_items_when_user_id_matches(
        conversation_repository: ConversationRepository,
        mock_redis_client: AsyncMock
) -> None:
    items = [{"role":"user", "content": "Hello"}]
    mock_redis_client.get.return_value = json.dumps({"user_id": "user1", "items": items})

    res = await conversation_repository.get("conversation2", "user1")

    assert res is not None
    assert res == items

    mock_redis_client.get.assert_awaited_with("conversation:conversation2")

async def test_save(conversation_repository: ConversationRepository, mock_redis_client: AsyncMock) -> None:

    await conversation_repository.save(
        "conversation1", "user1", [{"role":"user", "content": "Hello"}])

    mock_redis_client.set.assert_awaited_once()

    res = mock_redis_client.set.call_args[0][1]
    key = mock_redis_client.set.call_args[0][0]

    assert key == "conversation:conversation1"

    conv_ttl_sec = mock_redis_client.set.call_args.kwargs["ex"]

    assert conv_ttl_sec == settings.conversation_ttl_seconds

    data = json.loads(res)
    assert data["user_id"] == "user1"

