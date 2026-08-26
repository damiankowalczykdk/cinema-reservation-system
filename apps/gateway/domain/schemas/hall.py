from pydantic import BaseModel, ConfigDict


class CreateHall(BaseModel):
    cinema_id: int
    name: str
    rows: int
    seats_per_row: int

class UpdateHall(BaseModel):
    name: str | None = None
    rows: int | None = None
    seats_per_row: int | None = None


class HallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cinema_id: int
    name: str
    rows: int
    seats_per_row: int
