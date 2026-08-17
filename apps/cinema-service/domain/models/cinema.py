from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime
from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Cinema(Base):
    __tablename__ = "cinema"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(32), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Cinema: {self.name} city: {self.city} address: {self.address} >"


    def update(self, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

