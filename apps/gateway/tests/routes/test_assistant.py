import respx
from core.config import Auth0Settings
from domain.schemas.assistant import AssistantRequest
from httpx import AsyncClient, Response


@respx.mock
async def test_chat(
    client: AsyncClient, user_client: AsyncClient, test_settings: Auth0Settings
) -> None:
    payload = AssistantRequest(message="Test Message")

    respx.post(
        f"{test_settings.ai_service_url}/assistant",
        json=payload.model_dump(mode="json"),
    ).mock(
        return_value=Response(
            200,
            json={"answer": "Test Answer", "conversation_id": "resp_1"},
            headers={"X-User-Email": "test@example.com"},
        )
    )

    response = await user_client.post(
        "/assistants", json=payload.model_dump(mode="json")
    )

    assert response.status_code == 200
