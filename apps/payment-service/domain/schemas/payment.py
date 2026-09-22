from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict

class Status(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class CreatePayment(BaseModel):
    reservation_id: int
    guest_email: str | None = None

class CheckoutSessionRead(BaseModel):
    checkout_url: str | None

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