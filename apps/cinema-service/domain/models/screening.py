from datetime import UTC, datetime
from decimal import Decimal

from core.database import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column


class Screening(Base):
    __tablename__ = "screenings"
    __table_args__ = (
        Index("ix_screening_hall_id_start_time", "hall_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False
    )
    hall_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("halls.id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(6, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    )

    def __repr__(self) -> str:
        return f"< Screening {self.id} movie {self.movie_id} hall {self.hall_id} start_time {self.start_time} price {self.price} >"

    def update(self, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
