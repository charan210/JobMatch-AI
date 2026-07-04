from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_db
from app.repositories.exceptions import NotFoundError
from app.services.job_service import JobService

logger = get_logger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreateRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Backend Developer"})
    description: str = Field(..., json_schema_extra={"example": "FastAPI developer with PostgreSQL experience"})
    recruiter_id: UUID
    experience_required: int | None = Field(None, json_schema_extra={"example": 2})
    education_required: str | None = Field(None, json_schema_extra={"example": "Bachelor Degree"})
    status: str | None = Field(None, json_schema_extra={"example": "draft"})


class JobUpdateRequest(BaseModel):
    title: str | None = Field(None, json_schema_extra={"example": "Backend Engineer"})
    description: str | None = Field(None, json_schema_extra={"example": "Build REST APIs"})
    experience_required: int | None = Field(None, json_schema_extra={"example": 3})
    education_required: str | None = Field(None, json_schema_extra={"example": "Bachelor Degree"})
    status: str | None = Field(None, json_schema_extra={"example": "published"})


class JobResponse(BaseModel):
    id: UUID
    recruiter_id: UUID
    title: str
    description: str
    experience_required: int | None = None
    education_required: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobCreateResponse(BaseModel):
    job_id: UUID
    status: str


def get_job_service() -> JobService:
    return JobService()


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
    service: JobService = Depends(get_job_service),
) -> JobCreateResponse:
    logger.info("create_job_request_received", recruiter_id=str(payload.recruiter_id))
    try:
        job = await service.create_job(db, payload.model_dump(exclude_none=True))
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return JobCreateResponse(job_id=job.id, status="created")


@router.get("", response_model=list[JobResponse], status_code=status.HTTP_200_OK)
async def list_jobs(
    status: str | None = Query(None, description="Filter by job status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: JobService = Depends(get_job_service),
) -> list[JobResponse]:
    items, _ = await service.list_jobs(db, status=status, page=page, page_size=page_size)
    return [JobResponse.model_validate(item) for item in items]


@router.get("/{job_id}", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    try:
        job = await service.get_job(db, job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def update_job(
    job_id: UUID,
    payload: JobUpdateRequest,
    db: AsyncSession = Depends(get_db),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    try:
        job = await service.update_job(
            db,
            job_id,
            {k: v for k, v in payload.model_dump(exclude_none=True).items() if v is not None},
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: JobService = Depends(get_job_service),
) -> dict[str, str]:
    try:
        await service.delete_job(db, job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return {"job_id": str(job_id), "status": "deleted"}
