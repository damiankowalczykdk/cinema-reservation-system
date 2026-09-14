from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Integer, String, DateTime, Enum as SaEnum, Index
from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Status(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base):
    __tablename__ = 'payments'


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[Status] = mapped_column(SaEnum(Status), nullable=False)
    stripe_session_id: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    __table_args__ = Index(
        "uq_payment_reservation_active",
        "reservation_id",
        unique=True,
        postgresql_where=(status != "FAILED"),
    ),