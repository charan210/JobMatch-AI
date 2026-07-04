from __future__ import annotations

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.async_job import AsyncJob
from app.tasks.tasks import generate_ranking_task


class DummyRequest:
    id = "test-task-id"


class DummyTask:
    request = DummyRequest()


@pytest.mark.asyncio
async def test_generate_ranking_task_success(monkeypatch, async_session: AsyncSession) -> None:
    async_job_id = str(uuid4())
    job_id = str(uuid4())

    async_job = AsyncJob(
        id=async_job_id,
        job_type="ranking_generate",
        entity_type="job",
        entity_id=job_id,
        status="PENDING",
        payload_json={"job_id": job_id},
    )
    async_session.add(async_job)
    await async_session.flush()

    class FakeRankingService:
        async def generate_ranking(self, db, jid):
            assert str(jid) == job_id

    def fake_get_db_context():
        class DummyContext:
            async def __aenter__(self_inner):
                return async_session

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return DummyContext()

    monkeypatch.setattr("app.db.database.get_db_context", lambda: fake_get_db_context())
    monkeypatch.setattr("app.services.ranking_service.RankingService", lambda: FakeRankingService())
    monkeypatch.setattr("app.tasks.tasks.generate_ranking_task", DummyTask())

    # Patch the event loop to return the coroutine so we can await it in this async test
    class DummyLoop:
        def run_until_complete(self, coro):
            return coro
    monkeypatch.setattr("asyncio.get_event_loop", lambda: DummyLoop())

    result_coro = generate_ranking_task(async_job_id, job_id)
    result = await result_coro
    assert result["status"] == "completed"

    refreshed = await async_session.get(AsyncJob, async_job_id)
    assert refreshed is not None
    assert refreshed.status == "COMPLETED"
    assert refreshed.result_json == {"message": "ranking_complete"}
    assert refreshed.celery_task_id == "test-task-id"


@pytest.mark.asyncio
async def test_generate_ranking_task_failure(monkeypatch, async_session: AsyncSession) -> None:
    async_job_id = str(uuid4())
    job_id = str(uuid4())

    async_job = AsyncJob(
        id=async_job_id,
        job_type="ranking_generate",
        entity_type="job",
        entity_id=job_id,
        status="PENDING",
        payload_json={"job_id": job_id},
    )
    async_session.add(async_job)
    await async_session.flush()

    class FakeRankingService:
        async def generate_ranking(self, db, jid):
            raise RuntimeError("ranking failed")

    def fake_get_db_context():
        class DummyContext:
            async def __aenter__(self_inner):
                return async_session

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return DummyContext()

    monkeypatch.setattr("app.db.database.get_db_context", lambda: fake_get_db_context())
    monkeypatch.setattr("app.services.ranking_service.RankingService", lambda: FakeRankingService())
    monkeypatch.setattr("app.tasks.tasks.generate_ranking_task", DummyTask())

    # Patch the event loop to return the coroutine so we can await it in this async test
    class DummyLoop:
        def run_until_complete(self, coro):
            return coro
    monkeypatch.setattr("asyncio.get_event_loop", lambda: DummyLoop())

    with pytest.raises(RuntimeError, match="ranking failed"):
        await generate_ranking_task(async_job_id, job_id)

    refreshed = await async_session.get(AsyncJob, async_job_id)
    assert refreshed is not None
    assert refreshed.status == "FAILED"
    assert refreshed.error_message == "ranking failed"


def test_generate_ranking_task_celery_not_configured(monkeypatch) -> None:
    import importlib
    import app.tasks.tasks
    import app.tasks.celery_app
    
    # Mock celery_app as None
    monkeypatch.setattr(app.tasks.celery_app, "celery_app", None)
    
    # Reload the tasks module to evaluate the 'else' block
    importlib.reload(app.tasks.tasks)
    
    try:
        with pytest.raises(RuntimeError, match="Celery is not configured"):
            # Use the correct intended signature for the task
            app.tasks.tasks.generate_ranking_task("dummy_async_job_id", "dummy_job_id")
    finally:
        # Restore original state so subsequent tests don't fail
        monkeypatch.undo()
        importlib.reload(app.tasks.tasks)
