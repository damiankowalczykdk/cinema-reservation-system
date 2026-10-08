from fastapi import APIRouter
from agent.runner import run_agent
from api.dependencies import Service
from domain.schemas.assistant import AssistantRequest

router = APIRouter(prefix="/assistant", tags=["assistant ai"])

@router.post("")
async def chat(request: AssistantRequest, ai_service: Service):
    answer = await run_agent(
        message=request.message,
        ai_service=ai_service,
        previous_response_id=request.previous_response_id
    )

    return answer