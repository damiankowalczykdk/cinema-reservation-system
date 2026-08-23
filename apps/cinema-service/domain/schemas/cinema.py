from pydantic import BaseModel, ConfigDict


class CreateCinema(BaseModel):
    name: str
    city: str
    address: str

class UpdateCinema(BaseModel):
    name: str | None = None
    city: str | None = None
    address: str | None = None

class CinemaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    address: str


