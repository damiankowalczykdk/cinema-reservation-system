from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@patch("api.routes.assistant.run_agent", new_callable=AsyncMock)
async def test_chat(fake_run_agent: AsyncMock, client: AsyncClient) -> None:
    fake_run_agent.return_value = {"answer": "Test Answer", "response_id": "resp_1"}

    payload = {
        "message": "Test message"
    }

    response = await client.post("/assistant", json=payload)

    assert response.status_code == 200
    assert response.json() == {"answer": "Test Answer", "response_id": "resp_1"}