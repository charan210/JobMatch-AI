from __future__ import annotations

import enum
import uuid
from typing import Any

from sqlalchemy import (
    DateTime,
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base


class AsyncJobStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    STARTED = "STARTED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"


class AsyncJob(Base):
    __tablename__ = "async_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # type: ignore[assignment]
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AsyncJobStatus.PENDING.value)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=3)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    parent_job_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "payload": self.payload_json,
            "result": self.result_json,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
