from datetime import UTC, date, datetime
from enum import Enum

from core.database import Base
from sqlalchemy import Date, DateTime, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SaEnum
from sqlalchemy.orm import Mapped, mapped_column


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


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        UniqueConstraint("title", "release_date", name="uq_movie_title_release_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[Genre] = mapped_column(SaEnum(Genre), nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    poster_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trailer_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    )

    def __repr__(self) -> str:
        return (
            f"< Movie {self.id} title: {self.title} description: {self.description} duration: {self.duration_minutes}"
            f" genre: {self.genre} release_date: {self.release_date} >"
        )

    def update(self, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
