from core.config import settings
from core.rate_limit import limiter
from core.security import get_current_user
from domain.schemas.assistant import AssistantRequest, AssistantResponse
from domain.schemas.auth import TokenPayload
from fastapi import APIRouter, Depends, Request, status

from api.dependencies import AIServiceClient

router = APIRouter(prefix="/assistants", tags=["Assistant AI"])


@router.post("", response_model=AssistantResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    payload: AssistantRequest,
    ai_client: AIServiceClient,
    current_user: TokenPayload | None = Depends(get_current_user),
) -> AssistantResponse:
    headers: dict[str, str] | None = None
    if current_user:
        headers = {"X-User-Id": current_user.sub}
        if current_user.email:
            headers["X-User-Email"] = current_user.email

    return await ai_client.request(
        "POST",
        "/assistant",
        json=payload.model_dump(),
        timeout=settings.http_timeout_llm,
        headers=headers,
    )
