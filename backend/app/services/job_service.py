from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.repositories.pagination import PageParams
from app.repositories.sort import SortOrder, SortParams


class JobService:
    def __init__(
        self,
        repository: JobRepository | None = None,
        user_repository: Any | None = None,
    ) -> None:
        self.repository = repository or JobRepository()
        
        # Avoid circular imports if needed, but import here for clarity
        from app.repositories.user_repository import UserRepository
        self.user_repository = user_repository or UserRepository()

    async def create_job(self, db: AsyncSession, job_data: dict[str, Any]) -> Job:
        # Validate recruiter existence before persistence to prevent IntegrityError
        recruiter_id = job_data.get("recruiter_id")
        if recruiter_id:
            await self.user_repository.get_by_id_or_raise(db, recruiter_id)
            
        sanitized_data = {k: v for k, v in job_data.items() if v is not None}
        return await self.repository.create(db, sanitized_data)

    async def get_job(self, db: AsyncSession, job_id: object) -> Job:
        return await self.repository.get_by_id_or_raise(db, job_id)

    async def list_jobs(
        self,
        db: AsyncSession,
        status: str | None = None,
        page: int = 1,
        page_size: int = 25,
        sort_desc: bool = True,
    ) -> tuple[list[Job], int]:
        filters = {"status": status} if status is not None else None
        sort_params = SortParams(
            sort_by="created_at",
            sort_order=SortOrder.DESC if sort_desc else SortOrder.ASC,
        )
        page_params = PageParams(page=page, page_size=page_size)
        paginated = await self.repository.list(
            db,
            filters=filters,
            sort_params=sort_params,
            page_params=page_params,
        )
        return paginated.items, paginated.total

    async def update_job(self, db: AsyncSession, job_id: object, job_data: dict[str, Any]) -> Job:
        job = await self.get_job(db, job_id)
        return await self.repository.update(db, job, job_data)

    async def delete_job(self, db: AsyncSession, job_id: object) -> Job:
        job = await self.get_job(db, job_id)
        return await self.repository.delete(db, job)
