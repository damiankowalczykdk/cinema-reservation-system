from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from domain.models.reservation import Status


class CreateReservation(BaseModel):
    screening_id: int
    row: int
    seat: int
    guest_email: str | None = None
    guest_name: str | None = None

class UpdateReservation(BaseModel):
    screening_id: int
    row: int
    seat: int
    guest_email: str | None = None
    guest_name: str | None = None

class OccupiedSeatsRead(BaseModel):
    seats: list[tuple[int, int]]
    row: int
    seat_per_row: int

class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    screening_id: int
    user_id: str | None
    guest_email: str | None
    guest_name: str | None
    row: int
    seat: int
    status: Status
    price_paid: Decimal