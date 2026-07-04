from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_summary import AISummary
from app.repositories.base import BaseRepository


class AISummaryRepository(BaseRepository[AISummary]):
    def __init__(self) -> None:
        super().__init__(AISummary)

    async def get_by_candidate_and_job(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> AISummary | None:
        query = select(AISummary).where(
            AISummary.candidate_id == candidate_id,
            AISummary.job_id == job_id,
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def upsert(
        self,
        db: AsyncSession,
        *,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
        strengths: list[str],
        weaknesses: list[str],
        recommendation: str,
        summary_text: str,
        is_fallback: bool = False,
    ) -> AISummary:
        existing = await self.get_by_candidate_and_job(db, candidate_id, job_id)
        if existing is not None:
            existing.strengths = strengths
            existing.weaknesses = weaknesses
            existing.recommendation = recommendation
            existing.summary_text = summary_text
            existing.is_fallback = is_fallback
            await db.flush()
            return existing

        record = AISummary(
            candidate_id=candidate_id,
            job_id=job_id,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            summary_text=summary_text,
            is_fallback=is_fallback,
        )
        db.add(record)
        await db.flush()
        return record
