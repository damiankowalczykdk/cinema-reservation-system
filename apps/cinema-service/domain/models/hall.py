from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Hall(Base):
    __tablename__ = "halls"
    __table_args__ = (
        UniqueConstraint("cinema_id", "name", name="uq_hall_cinema_id_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cinema_id: Mapped[int] = mapped_column(ForeignKey("cinema.id"))
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    rows: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_per_row: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    def __repr__(self) -> str:
        return f"< Hall: {self.id} name: {self.name} rows: {self.rows} seats_per_row: {self.seats_per_row} >"


    def update(self, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)