from datetime import datetime
from decimal import Decimal
from core.config import settings
from pydantic import BaseModel, field_serializer, Field

class ReservationInfo(BaseModel):
    group_id: int
    guest_email: str | None = None

class AssistantResponse(BaseModel):
    answer: str
    conversation_id: str
    reservation: ReservationInfo | None = None
    seats_map_screening_id: int | None = None

class AssistantRequest(BaseModel):
    message: str = Field(max_length=1000)
    conversation_id: str | None = None

class ShowtimeRead(BaseModel):
    screening_id: int
    movie_title: str
    cinema_name: str
    city: str
    genre: str
    start_time: datetime
    price: Decimal

    @field_serializer("start_time")
    def format_start_time(self, value: datetime) -> str:
        return value.astimezone(settings.WARSAW).strftime("%A %Y-%m-%d %H:%M")

class SeatInput(BaseModel):
    row: int
    seat: int

class SeatMapRead(BaseModel):
    seats: list[tuple[int, int]]
    row: int
    seat_per_row: int

class CreateReservation(BaseModel):
    screening_id: int
    seats: list[SeatInput] = Field(min_length=1)
    guest_email: str | None = None
    guest_name: str | None = None


class ReservationRead(BaseModel):
    group_id: int
    screening_id: int
    guest_email: str | None
    row: int
    seat: int
    status: str
    price_paid: Decimal
    expires_at: datetime

    @field_serializer("expires_at")
    def format_expires_at(self, value: datetime) -> str:
        return value.astimezone(settings.WARSAW).strftime("%H:%M")


