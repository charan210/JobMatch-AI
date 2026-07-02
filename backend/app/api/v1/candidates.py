from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_db
from app.repositories.exceptions import NotFoundError
from app.services.candidate_service import CandidateService

logger = get_logger(__name__)
router = APIRouter(prefix="/candidates", tags=["Candidates"])


class CandidateCreateRequest(BaseModel):
    full_name: str = Field(..., json_schema_extra={"example": "Alice Smith"})
    email: str | None = Field(None, json_schema_extra={"example": "alice@example.com"})
    phone: str | None = Field(None, json_schema_extra={"example": "555-0100"})
    linkedin_url: str | None = Field(None, json_schema_extra={"example": "https://linkedin.com/in/alice"})
    experience_years: float | None = Field(None, json_schema_extra={"example": 3.5})
    education: str | None = Field(None, json_schema_extra={"example": "Bachelor of Science"})


class CandidateResponse(BaseModel):
    id: UUID
    full_name: str
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    experience_years: float | None = None
    education: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateCreateResponse(BaseModel):
    candidate_id: UUID
    status: str


def get_candidate_service() -> CandidateService:
    return CandidateService()


@router.post("", response_model=CandidateCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreateRequest,
    db: AsyncSession = Depends(get_db),
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateCreateResponse:
    logger.info("create_candidate_request_received", candidate=payload.full_name)
    candidate = await service.create_candidate(db, payload.model_dump(exclude_none=True))
    return CandidateCreateResponse(candidate_id=candidate.id, status="created")


@router.get("", response_model=list[CandidateResponse], status_code=status.HTTP_200_OK)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: CandidateService = Depends(get_candidate_service),
) -> list[CandidateResponse]:
    items, _ = await service.list_candidates(db, page=page, page_size=page_size)
    return [CandidateResponse.model_validate(item) for item in items]


@router.get("/{candidate_id}", response_model=CandidateResponse, status_code=status.HTTP_200_OK)
async def get_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateResponse:
    try:
        candidate = await service.get_candidate(db, candidate_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return CandidateResponse.model_validate(candidate)
