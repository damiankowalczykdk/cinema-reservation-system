from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CreateScreening(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime
    price: Decimal

class UpdateScreening(BaseModel):
    movie_id: int | None = None
    hall_id: int | None = None
    start_time: datetime | None = None
    price: Decimal | None = None

class SearchScreening(BaseModel):
    movie_id: int | None = None
    cinema_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

class SearchScreeningRead(BaseModel):
    screening_id: int
    movie_id: int
    movie_title: str
    cinema_id: int
    cinema_name: str
    hall_id: int
    start_time: datetime
    price: Decimal

class ScreeningRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    hall_id: int
    start_time: datetime
    price: Decimal