from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_score import CandidateScore
from app.repositories.candidate_score_repository import CandidateScoreRepository
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService


class RankingService:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        matching_service: MatchingService | None = None,
        repository: CandidateScoreRepository | None = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.matching_service = matching_service or MatchingService()
        self.repository = repository or CandidateScoreRepository()

    async def calculate_candidate_score(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> CandidateScore:
        candidate_embedding = await self.embedding_service.get_candidate_embedding(db, candidate_id)
        job_embedding = await self.embedding_service.get_job_embedding(db, job_id)

        semantic_score = await self.matching_service.compute_semantic_score(
            candidate_embedding.embedding if candidate_embedding else [],
            job_embedding.embedding if job_embedding else [],
        )
        skill_score = await self.matching_service.compute_skill_score(db, candidate_id, job_id)
        experience_score = await self.matching_service.compute_experience_score(db, candidate_id, job_id)
        education_score = await self.matching_service.compute_education_score(db, candidate_id, job_id)
        ai_score = 0.0

        final_score = round(
            (semantic_score * 0.35)
            + (skill_score * 0.25)
            + (experience_score * 0.20)
            + (education_score * 0.10)
            + (ai_score * 0.10),
            2,
        )
        recommendation = self._assign_recommendation(final_score)

        return await self.repository.upsert(
            db,
            candidate_id=candidate_id,
            job_id=job_id,
            skill_score=skill_score,
            experience_score=experience_score,
            education_score=education_score,
            semantic_score=semantic_score,
            ai_score=ai_score,
            final_score=final_score,
            rank_position=1,
            matched_skills=[],
            missing_skills=[],
            recommendation=recommendation,
        )

    async def get_score_breakdown(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> CandidateScore | None:
        return await self.repository.get_by_candidate_and_job(db, candidate_id, job_id)

    async def generate_ranking(self, db: AsyncSession, job_id: uuid.UUID) -> None:
        """Orchestrate ranking generation for a job by computing scores for all candidates
        and assigning rank positions. Idempotent if candidate_scores are upserted by
        (candidate_id, job_id).
        """
        # gather candidate ids
        from sqlalchemy import select
        from app.models.candidate import Candidate
        from app.models.candidate_score import CandidateScore

        result = await db.execute(select(Candidate.id))
        candidate_ids = [row[0] for row in result.fetchall()]

        for candidate_id in candidate_ids:
            await self.calculate_candidate_score(db, candidate_id, job_id)

        # Assign rank positions
        scores_result = await db.execute(select(CandidateScore).where(CandidateScore.job_id == job_id))
        scores = list(scores_result.scalars().all())
        # sort by final_score desc, then candidate_id asc
        scores.sort(key=lambda s: (-float(s.final_score or 0.0), str(s.candidate_id)))
        for idx, score in enumerate(scores, start=1):
            score.rank_position = idx
        await db.flush()

    def _assign_recommendation(self, final_score: float) -> str:
        if final_score >= 85:
            return "Highly Recommended"
        if final_score >= 65:
            return "Recommended"
        if final_score >= 45:
            return "Consider"
        return "Rejected"
