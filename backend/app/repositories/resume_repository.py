from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.repositories.base import BaseRepository
from app.repositories.exceptions import NotFoundError


class ResumeRepository(BaseRepository[Resume]):
    def __init__(self) -> None:
        super().__init__(Resume)

    async def get_by_id_or_raise(
        self,
        db: AsyncSession,
        resume_id: object,
    ) -> Resume:
        resume = await self.get_by_id(db, resume_id)
        if resume is None:
            raise NotFoundError("Resume", resume_id)
        return resume

    async def list_by_candidate(
        self,
        db: AsyncSession,
        candidate_id: object,
    ) -> list[Resume]:
        query = select(Resume).where(Resume.candidate_id == candidate_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(
        self,
        db: AsyncSession,
        resume_ids: Iterable[object],
    ) -> list[Resume]:
        query = select(Resume).where(Resume.id.in_(resume_ids))
        result = await db.execute(query)
        return list(result.scalars().all())
