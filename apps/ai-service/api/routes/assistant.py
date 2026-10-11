from typing import Annotated

from fastapi import APIRouter, Header
from agent.runner import run_agent
from api.dependencies import Service, User
from domain.schemas.assistant import AssistantRequest

router = APIRouter(prefix="/assistant", tags=["assistant ai"])

@router.post("")
async def chat(request: AssistantRequest, ai_service: Service, user_id: User = None):
    answer = await run_agent(
        message=request.message,
        ai_service=ai_service,
        previous_response_id=request.previous_response_id,
        user_id=user_id
    )

    return answer