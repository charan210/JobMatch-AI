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
