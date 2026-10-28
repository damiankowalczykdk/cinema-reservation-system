from uuid import uuid4

from agent.runner import run_agent
from domain.schemas.assistant import AssistantRequest, AssistantResponse
from fastapi import APIRouter

from api.dependencies import ConversationRepo, OpenAIClient, Service, User, UserEmail

router = APIRouter(prefix="/assistant", tags=["assistant ai"])


@router.post("")
async def chat(
    request: AssistantRequest,
    ai_service: Service,
    openai_client: OpenAIClient,
    conversation_repository: ConversationRepo,
    user_id: User = None,
    user_email: UserEmail = None,
) -> AssistantResponse:
    conversation_id = request.conversation_id or str(uuid4())
    history = await conversation_repository.get(conversation_id, user_id)
    if history is None:
        conversation_id = str(uuid4())
        history = []

    response, items = await run_agent(
        message=request.message,
        ai_service=ai_service,
        openai_client=openai_client,
        user_id=user_id,
        conversation_id=conversation_id,
        history=history,
        user_email=user_email,
    )

    await conversation_repository.save(conversation_id, user_id, items)

    return response
