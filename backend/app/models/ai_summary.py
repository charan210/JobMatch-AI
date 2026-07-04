from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.job import Job

class AISummary(Base):
    """Source: Data Governance & Database Design (Day 6 extensions)"""
    __tablename__ = "ai_summaries"

    candidate_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    strengths: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default='[]')
    weaknesses: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default='[]')
    recommendation: Mapped[str] = mapped_column(sa.Text, nullable=False)
    summary_text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    
    is_fallback: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False, server_default=sa.text('false'))

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", lazy="raise")
    job: Mapped["Job"] = relationship("Job", lazy="raise")

    __table_args__ = (
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_ai_summaries_candidate_job"),
    )

    def __repr__(self) -> str:
        return f"<AISummary(id={self.id}, candidate_id={self.candidate_id}, job_id={self.job_id})>"
