import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, MetaData, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tremor_api.config import DB_SCHEMA


class Base(DeclarativeBase):
    metadata = MetaData(schema=DB_SCHEMA)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    station: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="open")
    magnitude: Mapped[float | None] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
