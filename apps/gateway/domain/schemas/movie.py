from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict

class Genre(Enum):
    ACTION = "action"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    THRILLER = "thriller"
    ROMANCE = "romance"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"
    CRIME = "crime"
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    FAMILY = "family"
    WAR = "war"


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
