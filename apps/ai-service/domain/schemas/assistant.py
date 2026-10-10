from datetime import datetime
from core.config import settings
from pydantic import BaseModel, field_serializer


class AssistantRequest(BaseModel):
    message: str
    previous_response_id: str | None = None

class ShowtimeRead(BaseModel):
    screening_id: int
    movie_title: str
    cinema_name: str
    city: str
    genre: str
    start_time: datetime
    price: int

    @field_serializer("start_time")
    def format_start_time(self, value: datetime) -> str:
        return value.astimezone(settings.WARSAW).strftime("%A %Y-%m-%d %H:%M")

