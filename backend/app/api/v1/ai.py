import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.ai_schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    AISummaryResponse,
    InterviewQuestionResponse,
    SkillGapResponse,
)
from app.api.v1.jobs_status import AsyncJobResponse
from app.services.ai_pipeline_service import AIPipelineService
from app.services.async_job_service import AsyncJobService
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService
from app.tasks.tasks import generate_ai_artifacts_task

router = APIRouter()


@router.post(
    "/generate",
    response_model=AIGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_ai_artifacts(
    request: AIGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    candidate_service = CandidateService()
    job_service = JobService()
    pipeline_service = AIPipelineService()
    async_job_service = AsyncJobService()

    # Validate existence
    candidate = await candidate_service.get_candidate(db, request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = await job_service.get_job(db, request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Idempotency Check
    idempotency_result = await pipeline_service.check_idempotency(
        db, request.candidate_id, request.job_id
    )
    if idempotency_result:
        if idempotency_result["status"] == "COMPLETED":
            return AIGenerateResponse(
                job_id=idempotency_result["job_id"] or "COMPLETED_PREVIOUSLY",
                status="COMPLETED",
                status_url=f"/api/v1/ai/jobs/{idempotency_result['job_id']}" if idempotency_result["job_id"] else ""
            )
        else:
            return AIGenerateResponse(
                job_id=idempotency_result["job_id"],
                status=idempotency_result["status"],
                status_url=f"/api/v1/ai/jobs/{idempotency_result['job_id']}"
            )

    # Create new AsyncJob
    payload = {
        "candidate_id": str(request.candidate_id),
        "job_id": str(request.job_id),
    }
    async_job = await async_job_service.create_job(
        db,
        job_type="ai_generation",
        payload=payload,
        requested_by=str(current_user.id),
    )

    # Enqueue task
    generate_ai_artifacts_task.delay(async_job.id, str(request.candidate_id), str(request.job_id))

    return AIGenerateResponse(
        job_id=async_job.id,
        status=async_job.status,
        status_url=f"/api/v1/ai/jobs/{async_job.id}"
    )


@router.get("/jobs/{job_id}", response_model=AsyncJobResponse)
async def get_ai_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    async_job_service = AsyncJobService()
    job = await async_job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return AsyncJobResponse.model_validate(job.to_dict())


@router.get("/summary/{candidate_id}/{job_id}", response_model=AISummaryResponse)
async def get_ai_summary(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    pipeline_service = AIPipelineService()
    summary = await pipeline_service.summary_persistence.get_summary(db, candidate_id, job_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/interview/{candidate_id}/{job_id}", response_model=InterviewQuestionResponse)
async def get_ai_interview_questions(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    pipeline_service = AIPipelineService()
    questions = await pipeline_service.get_interview_questions(db, candidate_id, job_id)
    if not questions:
        raise HTTPException(status_code=404, detail="Interview questions not found")
    return questions


@router.get("/skill-gap/{candidate_id}/{job_id}", response_model=SkillGapResponse)
async def get_skill_gap(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    pipeline_service = AIPipelineService()
    try:
        gap = await pipeline_service.get_skill_gap(db, candidate_id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return gap
