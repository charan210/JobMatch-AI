from __future__ import annotations

from typing import Any
import traceback

from app.core.logging import get_logger
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)

if celery_app is not None:
    @celery_app.task(name="app.tasks.generate_ranking")
    def generate_ranking_task(async_job_id: str, job_id: str) -> dict[str, Any]:
        from app.db.database import get_db_context
        from app.models.async_job import AsyncJob
        from app.services.ranking_service import RankingService
        from sqlalchemy import func
        import uuid
        import asyncio

        async def _run() -> dict[str, Any]:
            async with get_db_context() as db:
                job = await db.get(AsyncJob, async_job_id)
                if job:
                    job.status = "STARTED"
                    job.started_at = func.now()  # type: ignore
                    job.celery_task_id = generate_ranking_task.request.id  # type: ignore
                    await db.flush()

                ranking_service = RankingService()
                try:
                    await ranking_service.generate_ranking(db, uuid.UUID(job_id))
                    if job:
                        job.status = "COMPLETED"
                        job.completed_at = func.now()  # type: ignore
                        job.result_json = {"message": "ranking_complete"}
                        await db.flush()
                    return {"status": "completed"}
                except Exception as exc:
                    logger.error("generate_ranking_failed", job_id=async_job_id, error=str(exc))
                    if job:
                        job.status = "FAILED"
                        job.error_message = str(exc)
                        await db.flush()
                    raise

        return asyncio.get_event_loop().run_until_complete(_run())

    @celery_app.task(name="app.tasks.parse_resume")
    def parse_resume_task(async_job_id: str, resume_id: str) -> dict[str, Any]:
        from app.db.database import get_db_context
        from app.services.async_job_service import AsyncJobService
        from app.services.resume_service import ResumeService
        from app.services.candidate_service import CandidateService
        from app.services.storage_service import get_storage_service
        from ai_engine.parsers.base_parser import BaseParser
        from ai_engine.parsers.pdf_parser import PdfParser
        from ai_engine.parsers.docx_parser import DocxParser
        from ai_engine.extractors.contact_extractor import ContactExtractor
        from ai_engine.extractors.skill_extractor import SkillExtractor
        import uuid
        import asyncio

        async def _run() -> dict[str, Any]:
            async with get_db_context() as db:
                job_svc = AsyncJobService()
                resume_svc = ResumeService()
                candidate_svc = CandidateService()
                
                try:
                    job = await job_svc.get_job(db, async_job_id)
                except Exception:
                    return {"status": "job_not_found"}

                if job.status == "COMPLETED":
                    return {"status": "already_completed"}
                
                await job_svc.update_job(
                    db, 
                    job_id=async_job_id, 
                    status="STARTED", 
                    celery_task_id=parse_resume_task.request.id  # type: ignore
                )

                try:
                    resume = await resume_svc.get_resume(db, uuid.UUID(resume_id))
                except Exception:
                    await job_svc.update_job(db, async_job_id, status="FAILED", error_message="Resume not found")
                    return {"status": "failed", "error": "Resume not found"}

                if resume.parsing_status == "COMPLETED":
                    await job_svc.update_job(
                        db, 
                        async_job_id, 
                        status="COMPLETED", 
                        result_json={"message": "resume already parsed"}
                    )
                    return {"status": "already_completed"}

                storage_service = get_storage_service()
                
                try:
                    # 1. Load file
                    file_obj = await storage_service.get_file(str(resume.file_url))
                    
                    # 2. Select Parser
                    text = ""
                    with file_obj:
                        parser: BaseParser
                        if resume.file_type == "application/pdf" or (resume.file_name and resume.file_name.lower().endswith(".pdf")):
                            parser = PdfParser()
                        elif resume.file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"] or (resume.file_name and resume.file_name.lower().endswith(".docx")):
                            parser = DocxParser()
                        else:
                            raise ValueError(f"Unsupported file type: {resume.file_type}")
                        
                        text = parser.parse(file_obj)

                    # 3. Extractors
                    contact_extractor = ContactExtractor()
                    skill_extractor = SkillExtractor()
                    
                    contacts = contact_extractor.extract(text)
                    skills = skill_extractor.extract(text)

                    # 4. Update Candidate using Service
                    await candidate_svc.update_candidate_from_parsing(
                        db, 
                        candidate_id=resume.candidate_id, 
                        contacts=contacts, 
                        skills=skills
                    )
                        
                    # 5. Update Statuses using Services
                    await resume_svc.update_resume_status(db, resume.id, status="COMPLETED")
                    
                    await job_svc.update_job(
                        db, 
                        async_job_id, 
                        status="COMPLETED", 
                        result_json={"contacts": contacts, "skills": skills}
                    )
                    
                    return {"status": "completed"}
                    
                except Exception as exc:
                    logger.error("parse_resume_failed", resume_id=resume_id, error=str(exc))
                    await resume_svc.update_resume_status(db, resume.id, status="FAILED")
                    await job_svc.update_job(db, async_job_id, status="FAILED", error_message=traceback.format_exc())
                    return {"status": "failed", "error": str(exc)}

        return asyncio.get_event_loop().run_until_complete(_run())

    @celery_app.task(name="app.tasks.generate_ai_artifacts")
    def generate_ai_artifacts_task(async_job_id: str, candidate_id: str, job_id: str) -> dict[str, Any]:
        from app.db.database import get_db_context
        from app.services.async_job_service import AsyncJobService
        from app.services.ai_pipeline_service import AIPipelineService
        import uuid
        import asyncio

        async def _run() -> dict[str, Any]:
            async with get_db_context() as db:
                job_svc = AsyncJobService()
                
                try:
                    job = await job_svc.get_job(db, async_job_id)
                except Exception:
                    return {"status": "job_not_found"}

                if job.status == "COMPLETED":
                    return {"status": "already_completed"}
                
                await job_svc.update_job(
                    db, 
                    job_id=async_job_id, 
                    status="STARTED", 
                    celery_task_id=generate_ai_artifacts_task.request.id  # type: ignore
                )

                pipeline_svc = AIPipelineService()
                try:
                    result = await pipeline_svc.execute_pipeline(
                        db, 
                        async_job_id=async_job_id, 
                        candidate_id=uuid.UUID(candidate_id), 
                        job_id=uuid.UUID(job_id)
                    )
                    return {"status": "completed", "result": result}
                except Exception as exc:
                    logger.error("generate_ai_artifacts_failed", async_job_id=async_job_id, error=str(exc))
                    # Pipeline service already updates the job status to FAILED
                    return {"status": "failed", "error": str(exc)}

        return asyncio.get_event_loop().run_until_complete(_run())

else:
    def generate_ranking_task(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("Celery is not configured.")
        
    def parse_resume_task(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("Celery is not configured.")

    def generate_ai_artifacts_task(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("Celery is not configured.")
