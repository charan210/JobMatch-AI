from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.logging import get_logger
from app.db.database import get_db
from app.services.async_job_service import AsyncJobService

logger = get_logger(__name__)
# The prefix is /jobs/status to align with GET /jobs/status/{job_id} requirements
router = APIRouter(prefix="/jobs/status", tags=["Jobs Status"])


class AsyncJobResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    entity_type: str | None = None
    entity_id: str | None = None
    attempts: int
    max_attempts: int
    payload: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


def get_async_job_service() -> AsyncJobService:
    return AsyncJobService()


@router.get("/{job_id}", response_model=AsyncJobResponse, status_code=status.HTTP_200_OK)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: AsyncJobService = Depends(get_async_job_service),
) -> AsyncJobResponse:
    """
    Retrieve the status of an asynchronous job by its ID.
    """
    # The service raises NotFoundError which is caught by global exception handlers
    job = await service.get_job(db, job_id)
    
    # We can rely on from_attributes=True to map ORM to Pydantic,
    # but the DB model has payload_json/result_json, while response expects payload/result.
    # The `to_dict()` on the model already maps this correctly, so we'll use that.
    return AsyncJobResponse.model_validate(job.to_dict())
