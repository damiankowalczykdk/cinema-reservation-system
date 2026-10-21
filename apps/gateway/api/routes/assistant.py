from fastapi import APIRouter, status, Depends, Request
from api.dependencies import AIServiceClient
from core.rate_limit import limiter
from core.security import get_current_user
from domain.schemas.assistant import AssistantRequest, AssistantResponse
from core.config import settings
from domain.schemas.auth import TokenPayload

router = APIRouter(prefix="/assistants", tags=["Assistant AI"])


@router.post("", response_model=AssistantResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def chat(
        request: Request,
        payload: AssistantRequest,
        ai_client: AIServiceClient,
        current_user: TokenPayload | None = Depends(get_current_user)
) -> AssistantResponse:

    headers: dict[str, str] | None = None
    if current_user:
        headers = {"X-User-Id": current_user.sub}
        if current_user.email:
            headers["X-User-Email"] = current_user.email

    return await ai_client.request(
        "POST",
        f"/assistant",
        json=payload.model_dump(),
        timeout=settings.http_timeout_llm,
        headers=headers
    )
