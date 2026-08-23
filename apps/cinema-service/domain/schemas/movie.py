from datetime import date
from pydantic import BaseModel, ConfigDict
from domain.models.movie import Genre


class CreateMovie(BaseModel):
    title: str
    description: str
    duration_minutes: int
    genre: Genre
    release_date: date

class UpdateMovie(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    genre: Genre | None = None
    release_date: date | None = None

class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    duration_minutes: int
    genre: Genre
    release_date: date
