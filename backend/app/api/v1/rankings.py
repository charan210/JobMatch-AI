from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_db

from app.models.async_job import AsyncJob
from app.repositories.candidate_score_repository import CandidateScoreRepository

logger = get_logger(__name__)
router = APIRouter(prefix="/rankings", tags=["Rankings"])

@router.post("/generate/{job_id}", status_code=status.HTTP_202_ACCEPTED)
async def generate_ranking(job_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    # Ensure job exists
    from app.models.job import Job
    from app.tasks.celery_app import celery_app
    from app.tasks.tasks import generate_ranking_task

    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Idempotency: if an active ranking job already exists for this job_id,
    # return the existing async_job instead of creating a duplicate.
    active_states = ["PENDING", "QUEUED", "STARTED", "RETRYING"]
    # Use SQLAlchemy select to avoid textual SQL pitfalls
    from sqlalchemy import select
    query = await db.execute(
        select(AsyncJob.id, AsyncJob.status).where(
            AsyncJob.job_type == "ranking_generate",
            AsyncJob.entity_type == "job",
            AsyncJob.entity_id == str(job_id),
            AsyncJob.status.in_(active_states),
        )
    )
    existing = query.first()
    if existing:
        return {"success": True, "message": "Job already queued", "data": {"job_id": existing[0], "status": existing[1]}}

    # Create async_jobs record
    async_job = AsyncJob(
        job_type="ranking_generate",
        entity_type="job",
        entity_id=str(job_id),
        status="PENDING",
        payload_json={"job_id": str(job_id)},
    )
    db.add(async_job)
    await db.flush()

    # Dispatch Celery task (guarded)
    if celery_app is None:
        # leave job as PENDING and inform caller that async worker is not configured
        return {"success": False, "message": "Async worker not configured", "data": {"job_id": async_job.id, "status": async_job.status}}

    await db.commit()
    celery_result = generate_ranking_task.apply_async(args=[async_job.id, str(job_id)])
    # update async job with celery task id and queued status
    async_job.celery_task_id = celery_result.id
    async_job.status = "QUEUED"
    await db.flush()

    return {"success": True, "message": "Job accepted", "data": {"job_id": async_job.id, "status": async_job.status, "job_type": async_job.job_type}}


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_rankings(job_id: UUID, db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    # Returns persisted candidate_scores for a job sorted by final_score desc
    from sqlalchemy import text
    query = await db.execute(
        text("SELECT * FROM candidate_scores WHERE job_id = :job_id ORDER BY final_score DESC, candidate_id ASC"),
        {"job_id": str(job_id)},
    )
    rows = query.mappings().fetchall()
    results = []
    for row in rows:
        # row is RowMapping; map expected fields
        results.append({
            "rank": row["rank_position"],
            "candidate_id": row["candidate_id"],
            "final_score": float(row["final_score"]),
            "recommendation": row["recommendation"],
        })
    return results


@router.get("/{job_id}/{candidate_id}", status_code=status.HTTP_200_OK)
async def get_score_breakdown(job_id: UUID, candidate_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    repo = CandidateScoreRepository()
    record = await repo.get_by_candidate_and_job(db, candidate_id, job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Score not found")
    return {
        "candidate_id": str(record.candidate_id),
        "job_id": str(record.job_id),
        "skill_score": float(record.skill_score or 0.0),
        "experience_score": float(record.experience_score or 0.0),
        "education_score": float(record.education_score or 0.0),
        "semantic_score": float(record.semantic_score or 0.0),
        "ai_score": float(record.ai_score or 0.0),
        "final_score": float(record.final_score or 0.0),
        "rank_position": int(record.rank_position or 0),
        "recommendation": record.recommendation,
    }
