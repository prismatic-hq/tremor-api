import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertCreate(BaseModel):
    station: str = Field(min_length=1, max_length=64)
    severity: Severity
    magnitude: float | None = Field(default=None, ge=-2, le=10)
    message: str = Field(min_length=1)


class AlertUpdate(BaseModel):
    severity: Severity | None = None
    status: AlertStatus | None = None
    magnitude: float | None = Field(default=None, ge=-2, le=10)
    message: str | None = Field(default=None, min_length=1)


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    station: str
    severity: Severity
    status: AlertStatus
    magnitude: float | None
    message: str
    created_at: datetime
    updated_at: datetime
