import pytest
from httpx import AsyncClient
from uuid import uuid4
from typing import Any

from app.models.async_job import AsyncJob, AsyncJobStatus

@pytest.mark.asyncio
async def test_get_job_status_success(client: AsyncClient, async_session: Any):
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
    
    response = await client.get(f"/jobs/status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == AsyncJobStatus.PENDING.value
    assert data["job_type"] == "parse_resume"

@pytest.mark.asyncio
async def test_get_job_status_not_found(client: AsyncClient):
    job_id = str(uuid4())
    response = await client.get(f"/jobs/status/{job_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()
