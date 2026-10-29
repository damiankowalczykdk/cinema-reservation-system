from unittest.mock import AsyncMock, patch

from domain.schemas.assistant import AssistantResponse
from httpx import AsyncClient


@patch("api.routes.assistant.run_agent", new_callable=AsyncMock)
async def test_chat(
    fake_run_agent: AsyncMock, client: AsyncClient, conversation_repository: AsyncMock
) -> None:
    fake_run_agent.return_value = (
        AssistantResponse(answer="Test Response", conversation_id="conversation_id"),
        [{"role": "user", "content": "Test Message"}],
    )

    payload = {
        "message": "Test message",
        "conversation_id": "conversation_id",
    }

    response = await client.post("/assistant", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Test Response",
        "conversation_id": "conversation_id",
        "reservation": None,
        "seats_map_screening_id": None,
    }


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")

    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "ai-service"
