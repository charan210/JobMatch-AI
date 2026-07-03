from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.pagination import PageParams
from app.repositories.sort import SortOrder, SortParams


class CandidateService:
    def __init__(self, repository: CandidateRepository | None = None) -> None:
        self.repository = repository or CandidateRepository()

    async def create_candidate(self, db: AsyncSession, candidate_data: dict[str, Any]) -> Candidate:
        sanitized_data = {k: v for k, v in candidate_data.items() if v is not None}
        return await self.repository.create(db, sanitized_data)

    async def get_candidate(self, db: AsyncSession, candidate_id: object) -> Candidate:
        return await self.repository.get_by_id_or_raise(db, candidate_id)

    async def list_candidates(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 25,
        sort_desc: bool = True,
    ) -> tuple[list[Candidate], int]:
        sort_params = SortParams(
            sort_by="created_at",
            sort_order=SortOrder.DESC if sort_desc else SortOrder.ASC,
        )
        page_params = PageParams(page=page, page_size=page_size)
        paginated = await self.repository.list(
            db,
            sort_params=sort_params,
            page_params=page_params,
        )
        return paginated.items, paginated.total

    async def update_candidate_from_parsing(
        self,
        db: AsyncSession,
        candidate_id: object,
        contacts: dict[str, Any],
        skills: list[str],
    ) -> Candidate:
        from app.repositories.skill_repository import SkillRepository
        from app.repositories.candidate_skill_repository import CandidateSkillRepository
        
        candidate = await self.get_candidate(db, candidate_id)
        
        update_data = {}
        if contacts.get("email") and not candidate.email:
            update_data["email"] = contacts["email"]
        if contacts.get("phone") and not candidate.phone:
            update_data["phone"] = contacts["phone"]
        if contacts.get("linkedin") and not candidate.linkedin_url:
            update_data["linkedin_url"] = contacts["linkedin"]
            
        if update_data:
            candidate = await self.repository.update(db, candidate, update_data)
            
        skill_repo = SkillRepository()
        cs_repo = CandidateSkillRepository()
        
        for skill_val in skills:
            skill = await skill_repo.get_or_create(db, skill_name=skill_val, category="extracted")
            existing_cs = await cs_repo.get_by_candidate_and_skill(db, candidate.id, skill.id)
            if not existing_cs:
                await cs_repo.create(db, {"candidate_id": candidate.id, "skill_id": skill.id})
                
        return candidate
