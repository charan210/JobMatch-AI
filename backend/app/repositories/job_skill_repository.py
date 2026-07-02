from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_skill import JobSkill
from app.repositories.base import BaseRepository
from app.repositories.exceptions import NotFoundError


class JobSkillRepository(BaseRepository[JobSkill]):
    def __init__(self) -> None:
        super().__init__(JobSkill)

    async def get_by_id_or_raise(
        self,
        db: AsyncSession,
        job_skill_id: object,
    ) -> JobSkill:
        job_skill = await self.get_by_id(db, job_skill_id)
        if job_skill is None:
            raise NotFoundError("JobSkill", job_skill_id)
        return job_skill

    async def get_by_job_and_skill(
        self,
        db: AsyncSession,
        job_id: object,
        skill_id: object,
    ) -> JobSkill | None:
        query = select(JobSkill).where(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id,
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def list_by_job(
        self,
        db: AsyncSession,
        job_id: object,
    ) -> list[JobSkill]:
        query = select(JobSkill).where(JobSkill.job_id == job_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def list_by_skill(
        self,
        db: AsyncSession,
        skill_id: object,
    ) -> list[JobSkill]:
        query = select(JobSkill).where(JobSkill.skill_id == skill_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(
        self,
        db: AsyncSession,
        job_skill_ids: Iterable[object],
    ) -> list[JobSkill]:
        query = select(JobSkill).where(JobSkill.id.in_(job_skill_ids))
        result = await db.execute(query)
        return list(result.scalars().all())
