from __future__ import annotations

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.candidate import Candidate
from app.models.async_job import AsyncJob
from app.models.candidate_score import CandidateScore
from app.models.user import User


@pytest.mark.asyncio
async def test_generate_ranking_creates_async_job_and_queues(async_session: AsyncSession, monkeypatch) -> None:
    # create user/candidate/job
    user = User(name="Test", email="t@example.com", password_hash="x", role="RECRUITER")
    async_session.add(user)
    await async_session.flush()
    job = Job(recruiter_id=user.id, title="SWE", description="desc")
    candidate = Candidate(full_name="Alice", email="a@example.com")
    async_session.add_all([job, candidate])
    await async_session.flush()

    # Monkeypatch Celery apply_async to simulate queuing
    class FakeResult:
        def __init__(self, id):
            self.id = id

    async def fake_apply_async(args=[], kwargs=None):
        return FakeResult("fake-task-id")

    # Patch the imported task in the tasks module to simulate Celery apply_async
    import app.tasks.tasks as tasks_module
    class FakeTask:
        def apply_async(self, args=None, kwargs=None):
            return FakeResult("fake-task-id")

    monkeypatch.setattr(tasks_module, "generate_ranking_task", FakeTask())
    # Ensure celery_app is present so the API dispatches (we don't need a real Celery)
    import app.tasks.celery_app as celery_app_module
    monkeypatch.setattr(celery_app_module, "celery_app", object())

    import app.api.v1.rankings as rankings_module

    client_job_id = job.id
    # Call the router function directly
    response = await rankings_module.generate_ranking(client_job_id, db=async_session)
    assert response["success"] is True
    data = response["data"]
    # Async job should be created
    async_job = await async_session.get(AsyncJob, data["job_id"])
    assert async_job is not None
    assert async_job.status in ("PENDING", "QUEUED")
    assert async_job.payload_json is not None
    assert async_job.payload_json["job_id"] == str(job.id)

    # No candidate_scores should be created synchronously
    from sqlalchemy import select, func
    result = await async_session.execute(select(func.count()).select_from(CandidateScore).where(CandidateScore.job_id == str(job.id)))
    count = result.scalar_one()
    assert count == 0


@pytest.mark.asyncio
async def test_duplicate_generate_ranking_returns_existing(async_session: AsyncSession, monkeypatch) -> None:
    # create job
    user = User(name="Test2", email="t2@example.com", password_hash="x", role="RECRUITER")
    async_session.add(user)
    await async_session.flush()
    job = Job(recruiter_id=user.id, title="SWE2", description="desc")
    async_session.add(job)
    await async_session.flush()

    # Insert an active async_job for this job
    existing = AsyncJob(job_type="ranking_generate", entity_type="job", entity_id=str(job.id), status="QUEUED", payload_json={"job_id": str(job.id)})
    async_session.add(existing)
    await async_session.flush()

    import app.api.v1.rankings as rankings_module
    resp = await rankings_module.generate_ranking(job.id, db=async_session)
    assert resp["success"] is True
    assert resp["message"] == "Job already queued"
    assert resp["data"]["job_id"] == existing.id
