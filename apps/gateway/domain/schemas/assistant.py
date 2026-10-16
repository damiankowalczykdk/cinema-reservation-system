from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(max_length=1000)
    conversation_id: str | None = None

class ReservationInfo(BaseModel):
    group_id: int
    guest_email: str | None

class AssistantResponse(BaseModel):
    answer: str
    conversation_id: str
    reservation: ReservationInfo | None = None
    seats_map_screening_id: int | None = None