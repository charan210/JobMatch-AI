from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_skill import CandidateSkill
from app.repositories.base import BaseRepository
from app.repositories.exceptions import NotFoundError


class CandidateSkillRepository(BaseRepository[CandidateSkill]):
    def __init__(self) -> None:
        super().__init__(CandidateSkill)

    async def get_by_id_or_raise(
        self,
        db: AsyncSession,
        candidate_skill_id: object,
    ) -> CandidateSkill:
        candidate_skill = await self.get_by_id(db, candidate_skill_id)
        if candidate_skill is None:
            raise NotFoundError("CandidateSkill", candidate_skill_id)
        return candidate_skill

    async def get_by_candidate_and_skill(
        self,
        db: AsyncSession,
        candidate_id: object,
        skill_id: object,
    ) -> Optional[CandidateSkill]:
        query = select(CandidateSkill).where(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_id,
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def list_by_candidate(
        self,
        db: AsyncSession,
        candidate_id: object,
    ) -> list[CandidateSkill]:
        query = select(CandidateSkill).where(CandidateSkill.candidate_id == candidate_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def list_by_skill(
        self,
        db: AsyncSession,
        skill_id: object,
    ) -> list[CandidateSkill]:
        query = select(CandidateSkill).where(CandidateSkill.skill_id == skill_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(
        self,
        db: AsyncSession,
        candidate_skill_ids: Iterable[object],
    ) -> list[CandidateSkill]:
        query = select(CandidateSkill).where(CandidateSkill.id.in_(candidate_skill_ids))
        result = await db.execute(query)
        return list(result.scalars().all())
