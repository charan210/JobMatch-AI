import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

from app.services.ai_pipeline_service import AIPipelineService
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ai_summary import AISummary

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def pipeline_service():
    return AIPipelineService()

@pytest.fixture
def sample_uuids():
    return {
        "candidate_id": uuid.uuid4(),
        "job_id": uuid.uuid4(),
        "async_job_id": "job-123"
    }

@pytest.mark.asyncio
async def test_execute_pipeline_success(pipeline_service, mock_db, sample_uuids):
    # Setup mocks
    candidate = Candidate(id=sample_uuids["candidate_id"], experience_years=5, education="BS")
    candidate.candidate_skills = []
    job = Job(id=sample_uuids["job_id"], title="Developer", experience_required=3, education_required="BS")
    job.job_skills = []
    
    pipeline_service.candidate_service.get_candidate = AsyncMock(return_value=candidate)
    pipeline_service.job_service.get_job = AsyncMock(return_value=job)
    pipeline_service.async_job_service.update_job = AsyncMock()
    
    db_result_mock = MagicMock()
    db_result_mock.scalars().all.return_value = []
    mock_db.execute = AsyncMock(return_value=db_result_mock)
    
    pipeline_service.summary_persistence.get_summary = AsyncMock(return_value=None)
    pipeline_service.summary_persistence.save_summary = AsyncMock()
    
    # Mock AI responses
    from ai_engine.matching.skill_gap_service import SkillGapResult
    skill_gap_result = SkillGapResult(matching_skills=[], missing_skills=["Python"], match_percentage=0.0)
    pipeline_service.skill_gap_service.analyze = MagicMock(return_value=skill_gap_result)
    
    summary_obj = MagicMock(strengths=["A"], weaknesses=["B"], recommendation="Consider", summary_text="Text", is_fallback=False)
    pipeline_service.summary_service.generate_summary = AsyncMock(return_value=summary_obj)
    
    interview_obj = MagicMock(questions=[], is_fallback=False)
    pipeline_service.interview_service.generate_questions = AsyncMock(return_value=interview_obj)

    # Execute
    result = await pipeline_service.execute_pipeline(mock_db, sample_uuids["async_job_id"], sample_uuids["candidate_id"], sample_uuids["job_id"])
    
    assert "skill_gap" in result
    assert "summary" in result
    assert "interview_questions" in result
    
    # Verify sequential updates
    update_calls = pipeline_service.async_job_service.update_job.call_args_list
    statuses = [call.kwargs.get('status') for call in update_calls]
    assert statuses == ["PROCESSING_SKILL_GAP", "PROCESSING_SUMMARY", "PROCESSING_INTERVIEW", "COMPLETED"]

@pytest.mark.asyncio
async def test_execute_pipeline_idempotency_summary_exists(pipeline_service, mock_db, sample_uuids):
    candidate = Candidate(id=sample_uuids["candidate_id"], experience_years=5, education="BS")
    candidate.candidate_skills = []
    job = Job(id=sample_uuids["job_id"], title="Developer", experience_required=3, education_required="BS")
    job.job_skills = []
    
    pipeline_service.candidate_service.get_candidate = AsyncMock(return_value=candidate)
    pipeline_service.job_service.get_job = AsyncMock(return_value=job)
    pipeline_service.async_job_service.update_job = AsyncMock()
    
    db_result_mock = MagicMock()
    db_result_mock.scalars().all.return_value = []
    mock_db.execute = AsyncMock(return_value=db_result_mock)
    
    existing_summary = AISummary(strengths=["X"], weaknesses=[], recommendation="Recommended", summary_text="Prev", is_fallback=False)
    pipeline_service.summary_persistence.get_summary = AsyncMock(return_value=existing_summary)
    pipeline_service.summary_persistence.save_summary = AsyncMock()
    
    from ai_engine.matching.skill_gap_service import SkillGapResult
    pipeline_service.skill_gap_service.analyze = MagicMock(return_value=SkillGapResult([], [], 100.0))
    pipeline_service.summary_service.generate_summary = AsyncMock()
    pipeline_service.interview_service.generate_questions = AsyncMock(return_value=MagicMock(questions=[], is_fallback=False))

    result = await pipeline_service.execute_pipeline(mock_db, sample_uuids["async_job_id"], sample_uuids["candidate_id"], sample_uuids["job_id"])
    
    pipeline_service.summary_service.generate_summary.assert_not_called()
    pipeline_service.summary_persistence.save_summary.assert_not_called()
    assert result["summary"]["summary_text"] == "Prev"

@pytest.mark.asyncio
async def test_execute_pipeline_repository_exception(pipeline_service, mock_db, sample_uuids):
    pipeline_service.candidate_service.get_candidate = AsyncMock(side_effect=Exception("DB Error"))
    pipeline_service.async_job_service.update_job = AsyncMock()
    
    with pytest.raises(Exception, match="DB Error"):
        await pipeline_service.execute_pipeline(mock_db, sample_uuids["async_job_id"], sample_uuids["candidate_id"], sample_uuids["job_id"])
        
    pipeline_service.async_job_service.update_job.assert_called_with(mock_db, sample_uuids["async_job_id"], status="FAILED", error_message="DB Error")
