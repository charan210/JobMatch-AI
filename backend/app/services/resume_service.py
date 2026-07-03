from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.repositories.pagination import PageParams
from app.repositories.sort import SortOrder, SortParams


class ResumeService:
    def __init__(self, repository: ResumeRepository | None = None) -> None:
        self.repository = repository or ResumeRepository()

    async def create_resume(self, db: AsyncSession, resume_data: dict[str, Any]) -> Resume:
        sanitized_data = {k: v for k, v in resume_data.items() if v is not None}
        return await self.repository.create(db, sanitized_data)

    async def get_resume(self, db: AsyncSession, resume_id: object) -> Resume:
        return await self.repository.get_by_id_or_raise(db, resume_id)

    async def list_resumes(
        self,
        db: AsyncSession,
        candidate_id: object | None = None,
        page: int = 1,
        page_size: int = 25,
        sort_desc: bool = True,
    ) -> tuple[list[Resume], int]:
        filters = {"candidate_id": candidate_id} if candidate_id is not None else None
        sort_params = SortParams(
            sort_by="uploaded_at",
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

    async def update_resume_status(self, db: AsyncSession, resume_id: object, status: str) -> Resume:
        resume = await self.get_resume(db, resume_id)
        return await self.repository.update(db, resume, {"parsing_status": status})
