from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.async_job import AsyncJob
from app.repositories.async_job_repository import AsyncJobRepository
from app.core.exceptions import NotFoundError


class AsyncJobService:
    def __init__(self) -> None:
        self.repository = AsyncJobRepository(AsyncJob)

    async def get_job(self, db: AsyncSession, job_id: str | UUID) -> AsyncJob:
        """
        Retrieve an async job by its ID. Raises NotFoundError if it does not exist.
        """
        job = await self.repository.get_by_id(db, str(job_id))
        if not job:
            raise NotFoundError(resource="AsyncJob", identifier=str(job_id))
        return job

    async def update_job(
        self,
        db: AsyncSession,
        job_id: str | UUID,
        status: str,
        celery_task_id: str | None = None,
        error_message: str | None = None,
        result_json: dict | None = None,
    ) -> AsyncJob:
        from sqlalchemy import func
        job = await self.get_job(db, job_id)
        update_data = {"status": status}
        if status == "STARTED" and not job.started_at:
            update_data["started_at"] = func.now()  # type: ignore
        if status == "COMPLETED" and not job.completed_at:
            update_data["completed_at"] = func.now()  # type: ignore
        if celery_task_id:
            update_data["celery_task_id"] = celery_task_id
        if error_message:
            update_data["error_message"] = error_message
        if result_json:
            update_data["result_json"] = result_json
            
        return await self.repository.update(db, job, update_data)
