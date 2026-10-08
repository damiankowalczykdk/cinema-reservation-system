from pydantic import BaseModel

class AssistantRequest(BaseModel):
    message: str
    previous_response_id: str | None = None

class AssistantResponse(BaseModel):
    answer: str
    response_id: str