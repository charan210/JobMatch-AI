from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.repositories.base import BaseRepository
from app.repositories.exceptions import NotFoundError


class JobRepository(BaseRepository[Job]):
    def __init__(self) -> None:
        super().__init__(Job)

    async def get_by_id_or_raise(
        self,
        db: AsyncSession,
        job_id: object,
    ) -> Job:
        job = await self.get_by_id(db, job_id)
        if job is None:
            raise NotFoundError("Job", job_id)
        return job

    async def list_by_recruiter(
        self,
        db: AsyncSession,
        recruiter_id: object,
        status: str | None = None,
        sort_desc: bool = True,
    ) -> list[Job]:
        query = select(Job).where(Job.recruiter_id == recruiter_id)
        if status is not None:
            query = query.where(Job.status == status)
        query = query.order_by(Job.created_at.desc() if sort_desc else Job.created_at.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(
        self,
        db: AsyncSession,
        job_ids: Iterable[object],
    ) -> list[Job]:
        query = select(Job).where(Job.id.in_(job_ids))
        result = await db.execute(query)
        return list(result.scalars().all())
