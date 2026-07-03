import pytest
from uuid import uuid4
from typing import Any

from app.models.async_job import AsyncJob, AsyncJobStatus
from app.services.async_job_service import AsyncJobService
from app.core.exceptions import NotFoundError

@pytest.mark.asyncio
async def test_get_job_success(async_session: Any):
    job_id = str(uuid4())
    job = AsyncJob(
        id=job_id,
        job_type="parse_resume",
        status=AsyncJobStatus.PENDING.value,
        priority=1,
        attempts=0,
        max_attempts=3
    )
    async_session.add(job)
    await async_session.commit()
    
    service = AsyncJobService()
    retrieved_job = await service.get_job(async_session, job_id)
    assert retrieved_job.id == job_id
    assert retrieved_job.job_type == "parse_resume"

@pytest.mark.asyncio
async def test_get_job_not_found(async_session: Any):
    service = AsyncJobService()
    job_id = str(uuid4())
    
    with pytest.raises(NotFoundError):
        await service.get_job(async_session, job_id)
