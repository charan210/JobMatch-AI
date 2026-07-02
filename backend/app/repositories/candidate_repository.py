from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.repositories.base import BaseRepository
from app.repositories.exceptions import NotFoundError


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self) -> None:
        super().__init__(Candidate)

    async def get_by_id_or_raise(
        self,
        db: AsyncSession,
        candidate_id: object,
    ) -> Candidate:
        candidate = await self.get_by_id(db, candidate_id)
        if candidate is None:
            raise NotFoundError("Candidate", candidate_id)
        return candidate

    async def list_by_emails(
        self,
        db: AsyncSession,
        emails: Iterable[str],
    ) -> list[Candidate]:
        query = select(Candidate).where(Candidate.email.in_(emails))
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[Candidate]:
        query = select(Candidate).where(Candidate.email == email)
        result = await db.execute(query)
        return result.scalars().first()
