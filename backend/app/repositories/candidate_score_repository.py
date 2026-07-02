from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_score import CandidateScore
from app.repositories.base import BaseRepository


class CandidateScoreRepository(BaseRepository[CandidateScore]):
    def __init__(self) -> None:
        super().__init__(CandidateScore)

    async def get_by_candidate_and_job(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> CandidateScore | None:
        query = select(CandidateScore).where(
            CandidateScore.candidate_id == candidate_id,
            CandidateScore.job_id == job_id,
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def upsert(
        self,
        db: AsyncSession,
        *,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
        skill_score: float | Decimal | None,
        experience_score: float | Decimal | None,
        education_score: float | Decimal | None,
        semantic_score: float | Decimal | None,
        ai_score: float | Decimal | None,
        final_score: float | Decimal | None,
        rank_position: int | None,
        matched_skills: list[str] | None,
        missing_skills: list[str] | None,
        recommendation: str | None,
    ) -> CandidateScore:
        def to_decimal(val: float | Decimal | None) -> Decimal | None:
            if val is None:
                return None
            return Decimal(str(val))

        existing = await self.get_by_candidate_and_job(db, candidate_id, job_id)
        if existing is not None:
            existing.skill_score = to_decimal(skill_score)
            existing.experience_score = to_decimal(experience_score)
            existing.education_score = to_decimal(education_score)
            existing.semantic_score = to_decimal(semantic_score)
            existing.ai_score = to_decimal(ai_score)
            existing.final_score = to_decimal(final_score)
            existing.rank_position = rank_position
            existing.matched_skills = matched_skills
            existing.missing_skills = missing_skills
            existing.recommendation = recommendation
            await db.flush()
            return existing

        record = CandidateScore(
            candidate_id=candidate_id,
            job_id=job_id,
            skill_score=to_decimal(skill_score),
            experience_score=to_decimal(experience_score),
            education_score=to_decimal(education_score),
            semantic_score=to_decimal(semantic_score),
            ai_score=to_decimal(ai_score),
            final_score=to_decimal(final_score),
            rank_position=rank_position,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            recommendation=recommendation,
        )
        db.add(record)
        await db.flush()
        return record
