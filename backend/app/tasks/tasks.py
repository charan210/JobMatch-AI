from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)

if celery_app is not None:
    @celery_app.task(name="app.tasks.generate_ranking")
    def generate_ranking_task(async_job_id: str, job_id: str) -> dict[str, Any]:
        # Import inside task to avoid heavy imports at module import time
        from app.db.database import get_db_context
        from app.models.async_job import AsyncJob
        from app.services.ranking_service import RankingService
        from sqlalchemy import func

        async def _run() -> dict[str, Any]:
            async with get_db_context() as db:
                # mark started
                job = await db.get(AsyncJob, async_job_id)
                if job:
                    job.status = "STARTED"
                    job.started_at = func.now()  # type: ignore
                    job.celery_task_id = generate_ranking_task.request.id  # type: ignore
                    await db.flush()

                ranking_service = RankingService()
                try:
                    import uuid
                    await ranking_service.generate_ranking(db, uuid.UUID(job_id))
                    if job:
                        job.status = "COMPLETED"
                        job.completed_at = func.now()  # type: ignore
                        job.result_json = {"message": "ranking_complete"}
                        await db.flush()
                    return {"status": "completed"}
                except Exception as exc:
                    logger.error("generate_ranking_failed", job_id=async_job_id, error=str(exc))
                    if job:
                        job.status = "FAILED"
                        job.error_message = str(exc)
                        await db.flush()
                    raise

        # Run the async coroutine from Celery (sync task entrypoint)
        import asyncio

        return asyncio.get_event_loop().run_until_complete(_run())
else:
    def generate_ranking_task(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("Celery is not configured. Install celery and a Redis broker to enable async tasks.")
