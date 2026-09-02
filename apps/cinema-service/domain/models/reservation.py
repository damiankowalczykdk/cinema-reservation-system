from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import Enum as SaEnum, Index
from sqlalchemy import Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Status(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Reservation(Base):
    __tablename__ = "reservations"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    screening_id: Mapped[int] = mapped_column(Integer, ForeignKey('screenings.id'), nullable=False)
    user_id: Mapped[str| None] = mapped_column(String(255))
    guest_email: Mapped[str | None] = mapped_column(String(255))
    guest_name: Mapped[str| None] = mapped_column(String(32))
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    seat: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(SaEnum(Status), nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(DECIMAL(6, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    __table_args__ = (
        Index(
            "uq_reservation_screening_row_seat_active",
            "screening_id", "row", "seat",
            unique=True,
            postgresql_where=(status != "CANCELLED"),
        )
    ),

    def __repr__(self) -> str:
        return (f"< Reservation {self.id} screening {self.screening_id} row {self.row} seat {self.seat} "
                f"status {self.status} price {self.price_paid} >")

    def update(self, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)


