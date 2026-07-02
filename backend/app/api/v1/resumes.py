from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_db
from app.repositories.exceptions import NotFoundError
from app.services.resume_service import ResumeService
from app.services.storage_service import StorageBackend, get_storage_service

logger = get_logger(__name__)
router = APIRouter(prefix="/resumes", tags=["Resumes"])


class ResumeResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    file_name: str
    file_url: str | None = None
    file_type: str | None = None
    file_size: int | None = None
    parsing_status: str
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeCreateResponse(BaseModel):
    resume_id: UUID
    status: str


def get_resume_service() -> ResumeService:
    return ResumeService()


ALLOWED_MIME_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=ResumeCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    candidate_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    resume_service: ResumeService = Depends(get_resume_service),
    storage_service: StorageBackend = Depends(get_storage_service),
) -> ResumeCreateResponse:
    logger.info("upload_resume_request_received", candidate_id=str(candidate_id), file_name=file.filename)
    
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {ALLOWED_MIME_TYPES}"
        )
        
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )

    # Persist file
    file_url = await storage_service.save_file(file.filename or "resume.pdf", file.file)
    
    # Create DB record
    resume_data = {
        "candidate_id": str(candidate_id),
        "file_name": file.filename or "resume.pdf",
        "file_url": file_url,
        "file_type": file.content_type,
        "file_size": file_size,
        "parsing_status": "PENDING"
    }
    resume = await resume_service.create_resume(db, resume_data)
    
    return ResumeCreateResponse(resume_id=resume.id, status="uploaded")


@router.get("", response_model=list[ResumeResponse], status_code=status.HTTP_200_OK)
async def list_resumes(
    candidate_id: UUID | None = Query(None, description="Filter resumes by candidate id"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: ResumeService = Depends(get_resume_service),
) -> list[ResumeResponse]:
    items, _ = await service.list_resumes(db, candidate_id=candidate_id, page=page, page_size=page_size)
    return [ResumeResponse.model_validate(item) for item in items]


@router.get("/{resume_id}", response_model=ResumeResponse, status_code=status.HTTP_200_OK)
async def get_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ResumeService = Depends(get_resume_service),
) -> ResumeResponse:
    try:
        resume = await service.get_resume(db, resume_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return ResumeResponse.model_validate(resume)
