from __future__ import annotations

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.async_job import AsyncJob
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.tasks.tasks import parse_resume_task


class DummyRequest:
    id = "test-task-id"


class DummyTask:
    request = DummyRequest()


class DummyFile:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_parse_resume_task_success(monkeypatch, async_session: AsyncSession) -> None:
    candidate_id = uuid4()
    candidate = Candidate(
        id=candidate_id,
        full_name="Test User",
        email=None,
        phone=None,
        linkedin_url=None
    )
    async_session.add(candidate)
    
    resume_id = uuid4()
    resume = Resume(
        id=resume_id,
        candidate_id=candidate_id,
        file_name="test.pdf",
        file_url="test.pdf",
        file_type="application/pdf",
        parsing_status="pending"
    )
    async_session.add(resume)
    
    async_job_id = str(uuid4())
    async_job = AsyncJob(
        id=async_job_id,
        job_type="parse_resume",
        entity_type="resume",
        entity_id=str(resume_id),
        status="PENDING"
    )
    async_session.add(async_job)
    await async_session.flush()

    class FakeStorageService:
        async def get_file(self, file_url):
            return DummyFile()

    class FakePdfParser:
        def parse(self, file_obj):
            return "Fake PDF Content"

    class FakeContactExtractor:
        def extract(self, text):
            return {"email": "test@example.com", "phone": "123456789", "linkedin": None}

    class FakeSkillExtractor:
        def extract(self, text):
            return ["Python", "AWS"]

    def fake_get_db_context():
        class DummyContext:
            async def __aenter__(self_inner):
                return async_session
            async def __aexit__(self_inner, exc_type, exc, tb):
                return False
        return DummyContext()

    monkeypatch.setattr("app.db.database.get_db_context", lambda: fake_get_db_context())
    monkeypatch.setattr("app.tasks.tasks.get_storage_service", lambda: FakeStorageService(), raising=False)
    monkeypatch.setattr("app.services.storage_service.get_storage_service", lambda: FakeStorageService())
    monkeypatch.setattr("ai_engine.parsers.pdf_parser.PdfParser", FakePdfParser)
    monkeypatch.setattr("ai_engine.extractors.contact_extractor.ContactExtractor", FakeContactExtractor)
    monkeypatch.setattr("ai_engine.extractors.skill_extractor.SkillExtractor", FakeSkillExtractor)
    monkeypatch.setattr("app.tasks.tasks.parse_resume_task", DummyTask())

    class DummyLoop:
        def run_until_complete(self, coro):
            return coro
    monkeypatch.setattr("asyncio.get_event_loop", lambda: DummyLoop())

    result_coro = parse_resume_task(async_job_id, str(resume_id))
    result = await result_coro
    assert result["status"] == "completed"

    refreshed_job = await async_session.get(AsyncJob, async_job_id)
    assert refreshed_job is not None
    assert refreshed_job.status == "COMPLETED"
    assert refreshed_job.result_json is not None
    assert refreshed_job.result_json["contacts"]["email"] == "test@example.com"
    assert "Python" in refreshed_job.result_json["skills"]

    refreshed_resume = await async_session.get(Resume, resume_id)
    assert refreshed_resume is not None
    assert refreshed_resume.parsing_status == "COMPLETED"

    refreshed_candidate = await async_session.get(Candidate, candidate_id)
    assert refreshed_candidate is not None
    assert refreshed_candidate.email == "test@example.com"
    assert refreshed_candidate.phone == "123456789"
