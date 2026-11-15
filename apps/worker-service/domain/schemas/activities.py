from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Seat(BaseModel):
    row: int
    seat: int


class ReservationSummary(BaseModel):
    start_time: datetime
    total_price: Decimal
    seats: list[Seat]
    ticket_code: str
    movie_title: str
    city: str
    hall_name: str
    currency: str
