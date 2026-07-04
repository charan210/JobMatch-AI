from __future__ import annotations

import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import get_logger
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService
from app.services.async_job_service import AsyncJobService
from app.services.ai_summary_persistence_service import AISummaryPersistenceService
from ai_engine.matching.skill_gap_service import SkillGapService
from ai_engine.summarization.summary_service import SummaryService
from ai_engine.interview_generation.interview_service import InterviewQuestionService

logger = get_logger(__name__)

class AIPipelineService:
    def __init__(self) -> None:
        self.candidate_service = CandidateService()
        self.job_service = JobService()
        self.async_job_service = AsyncJobService()
        self.summary_persistence = AISummaryPersistenceService()
        self.skill_gap_service = SkillGapService()
        self.summary_service = SummaryService()
        self.interview_service = InterviewQuestionService()

    async def check_idempotency(self, db: AsyncSession, candidate_id: uuid.UUID, job_id: uuid.UUID) -> dict[str, Any] | None:
        """Check if an AI generation job is already running or completed for this candidate and job."""
        # Check if completed
        existing_summary = await self.summary_persistence.get_summary(db, candidate_id, job_id)
        if existing_summary:
            return {"status": "COMPLETED", "job_id": None}
            
        # Check if running
        payload_match = {"candidate_id": str(candidate_id), "job_id": str(job_id)}
        query = select(self.async_job_service.repository.model).where(
            self.async_job_service.repository.model.job_type == "ai_generation",
            self.async_job_service.repository.model.status.in_(["PENDING", "QUEUED", "STARTED", "PROCESSING_SKILL_GAP", "PROCESSING_SUMMARY", "PROCESSING_INTERVIEW"])
        )
        result = await db.execute(query)
        running_jobs = result.scalars().all()
        
        for job in running_jobs:
            if job.payload_json == payload_match:
                return {"status": job.status, "job_id": job.id}
                
        return None

    async def get_interview_questions(self, db: AsyncSession, candidate_id: uuid.UUID, job_id: uuid.UUID) -> dict[str, Any] | None:
        """Retrieve interview questions. For now, this extracts them from the most recent AsyncJob result."""
        payload_match = {"candidate_id": str(candidate_id), "job_id": str(job_id)}
        query = select(self.async_job_service.repository.model).where(
            self.async_job_service.repository.model.job_type == "ai_generation",
            self.async_job_service.repository.model.status == "COMPLETED"
        ).order_by(self.async_job_service.repository.model.created_at.desc())
        
        result = await db.execute(query)
        completed_jobs = result.scalars().all()
        
        for job in completed_jobs:
            if job.payload_json == payload_match and job.result_json:
                return job.result_json.get("interview_questions")
                
        return None

    async def get_skill_gap(self, db: AsyncSession, candidate_id: uuid.UUID, job_id: uuid.UUID) -> dict[str, Any]:
        """Compute or retrieve the skill gap analysis dynamically."""
        candidate = await self.candidate_service.get_candidate(db, candidate_id)
        job = await self.job_service.get_job(db, job_id)
        
        if not candidate or not job:
            raise ValueError("Candidate or Job not found")

        from sqlalchemy.orm import selectinload
        from app.models.candidate_skill import CandidateSkill
        from app.models.job_skill import JobSkill

        c_skills_result = await db.execute(
            select(CandidateSkill).options(selectinload(CandidateSkill.skill)).where(CandidateSkill.candidate_id == candidate_id)
        )
        c_skills = [cs.skill.skill_name for cs in c_skills_result.scalars().all()]

        j_skills_result = await db.execute(
            select(JobSkill).options(selectinload(JobSkill.skill)).where(JobSkill.job_id == job_id)
        )
        j_skills = [js.skill.skill_name for js in j_skills_result.scalars().all()]

        candidate_profile = {
            "id": str(candidate.id),
            "experience_years": candidate.experience_years,
            "education": candidate.education,
            "skills": c_skills
        }
        job_profile = {
            "id": str(job.id),
            "title": job.title,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "skills": j_skills
        }
        
        from dataclasses import asdict
        from typing import cast
        c_skills = cast(list[str], candidate_profile["skills"])
        j_skills = cast(list[str], job_profile["skills"])
        result_obj = self.skill_gap_service.analyze(c_skills, j_skills)
        return asdict(result_obj)

    async def execute_pipeline(self, db: AsyncSession, async_job_id: str, candidate_id: uuid.UUID, job_id: uuid.UUID) -> dict[str, Any]:
        logger.info("ai_pipeline_started", async_job_id=async_job_id, candidate_id=str(candidate_id), job_id=str(job_id))
        
        try:
            # 1. Load profiles
            candidate = await self.candidate_service.get_candidate(db, candidate_id)
            job = await self.job_service.get_job(db, job_id)

            from sqlalchemy.orm import selectinload
            from app.models.candidate_skill import CandidateSkill
            from app.models.job_skill import JobSkill

            c_skills_result = await db.execute(
                select(CandidateSkill).options(selectinload(CandidateSkill.skill)).where(CandidateSkill.candidate_id == candidate_id)
            )
            c_skills = [cs.skill.skill_name for cs in c_skills_result.scalars().all()]

            j_skills_result = await db.execute(
                select(JobSkill).options(selectinload(JobSkill.skill)).where(JobSkill.job_id == job_id)
            )
            j_skills = [js.skill.skill_name for js in j_skills_result.scalars().all()]

            candidate_profile = {
                "id": str(candidate.id),
                "experience_years": candidate.experience_years,
                "education": candidate.education,
                "skills": c_skills
            }
            job_profile = {
                "id": str(job.id),
                "title": job.title,
                "experience_required": job.experience_required,
                "education_required": job.education_required,
                "skills": j_skills
            }

            # 2. Check existing (Idempotency)
            existing_summary = await self.summary_persistence.get_summary(db, candidate_id, job_id)
            
            # 3. Skill Gap
            await self.async_job_service.update_job(db, async_job_id, status="PROCESSING_SKILL_GAP")
            from dataclasses import asdict
            from typing import cast
            c_skills = cast(list[str], candidate_profile["skills"])
            j_skills = cast(list[str], job_profile["skills"])
            skill_gap_result_obj = self.skill_gap_service.analyze(c_skills, j_skills)
            skill_gap_result = asdict(skill_gap_result_obj)
            logger.info("skill_gap_completed", async_job_id=async_job_id)

            # 4. Summary
            await self.async_job_service.update_job(db, async_job_id, status="PROCESSING_SUMMARY")
            if existing_summary:
                summary_data = {
                    "strengths": existing_summary.strengths,
                    "weaknesses": existing_summary.weaknesses,
                    "recommendation": existing_summary.recommendation,
                    "summary_text": existing_summary.summary_text,
                    "is_fallback": existing_summary.is_fallback
                }
            else:
                summary_obj = await self.summary_service.generate_summary(candidate_profile, job_profile, skill_gap_result)
                summary_data = {
                    "strengths": summary_obj.strengths,
                    "weaknesses": summary_obj.weaknesses,
                    "recommendation": summary_obj.recommendation,
                    "summary_text": summary_obj.summary_text,
                    "is_fallback": summary_obj.is_fallback
                }
                # Persist summary
                await self.summary_persistence.save_summary(
                    db, candidate_id, job_id,
                    strengths=summary_obj.strengths,
                    weaknesses=summary_obj.weaknesses,
                    recommendation=summary_obj.recommendation,
                    summary_text=summary_obj.summary_text,
                    is_fallback=summary_obj.is_fallback
                )
            logger.info("summary_completed", async_job_id=async_job_id)

            # 5. Interview Questions
            # TODO: Milestone 6 - Create interview_questions persistence model.
            # For now, these are NOT permanently stored and only exist transiently in AsyncJob.result_json pipeline output.
            await self.async_job_service.update_job(db, async_job_id, status="PROCESSING_INTERVIEW")
            interview_obj = await self.interview_service.generate_questions(candidate_profile, job_profile, skill_gap_result)
            interview_data = {
                "questions": [q.model_dump() for q in interview_obj.questions],
                "is_fallback": interview_obj.is_fallback
            }
            logger.info("interview_completed", async_job_id=async_job_id)

            # 6. Update Async Job
            result = {
                "skill_gap": skill_gap_result,
                "summary": summary_data,
                "interview_questions": interview_data
            }
            
            await self.async_job_service.update_job(db, async_job_id, status="COMPLETED", result_json=result)
            logger.info("ai_pipeline_completed", async_job_id=async_job_id)
            return result
        
        except Exception as exc:
            logger.error("ai_pipeline_failed", async_job_id=async_job_id, error_type="pipeline_error")
            await self.async_job_service.update_job(db, async_job_id, status="FAILED", error_message=str(exc))
            raise
