from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_summary import AISummary
from app.repositories.ai_summary_repository import AISummaryRepository


class AISummaryPersistenceService:
    def __init__(self) -> None:
        self.repository = AISummaryRepository()

    async def get_summary(
        self, db: AsyncSession, candidate_id: uuid.UUID, job_id: uuid.UUID
    ) -> AISummary | None:
        return await self.repository.get_by_candidate_and_job(db, candidate_id, job_id)

    async def save_summary(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
        strengths: list[str],
        weaknesses: list[str],
        recommendation: str,
        summary_text: str,
        is_fallback: bool,
    ) -> AISummary:
        return await self.repository.upsert(
            db,
            candidate_id=candidate_id,
            job_id=job_id,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            summary_text=summary_text,
            is_fallback=is_fallback,
        )
