from fastapi import APIRouter, status
from api.dependencies import AIServiceClient
from domain.schemas.assistant import AssistantRequest, AssistantResponse
from core.config import settings

router = APIRouter(prefix="/assistants", tags=["Assistant AI"])

@router.post("", response_model=AssistantResponse, status_code=status.HTTP_200_OK)
async def chat(payload: AssistantRequest, ai_client: AIServiceClient) -> AssistantResponse:
    return await ai_client.request(
        "POST",
        f"/assistant",
        json=payload.model_dump(),
        timeout=settings.http_timeout_llm
    )
