from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from core.database import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey, Index, Integer, Sequence, String
from sqlalchemy import Enum as SaEnum
from sqlalchemy.orm import Mapped, mapped_column


class Status(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


reservation_group_id_seq = Sequence("reservation_group_id_seq", metadata=Base.metadata)


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    screening_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("screenings.id"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(String(255))
    guest_email: Mapped[str | None] = mapped_column(String(255))
    guest_name: Mapped[str | None] = mapped_column(String(32))
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    seat: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(SaEnum(Status), nullable=False)
    price_paid: Mapped[Decimal] = mapped_column(DECIMAL(6, 2), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    )

    __table_args__ = (
        (
            Index(
                "uq_reservation_screening_row_seat_active",
                "screening_id",
                "row",
                "seat",
                unique=True,
                postgresql_where=(status != "CANCELLED"),
            )
        ),
    )

    def __repr__(self) -> str:
        return (
            f"< Reservation {self.id} screening {self.screening_id} row {self.row} seat {self.seat} "
            f"status {self.status} price {self.price_paid} >"
        )
