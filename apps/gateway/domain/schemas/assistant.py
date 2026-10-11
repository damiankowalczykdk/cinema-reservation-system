from pydantic import BaseModel

class AssistantRequest(BaseModel):
    message: str
    previous_response_id: str | None = None

class ReservationInfo(BaseModel):
    group_id: int
    guest_email: str | None

class AssistantResponse(BaseModel):
    answer: str
    response_id: str
    reservation: ReservationInfo | None = None
    seats_map_screening_id: int | None = None