import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

from app.tasks.tasks import generate_ai_artifacts_task

@pytest.fixture
def mock_db_context():
    # Setup mock db context manager
    db_session_mock = AsyncMock()
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = db_session_mock
    return context_manager, db_session_mock

@patch("app.db.database.get_db_context")
@patch("app.services.async_job_service.AsyncJobService")
@patch("app.services.ai_pipeline_service.AIPipelineService")
def test_generate_ai_artifacts_task_success(mock_pipeline_cls, mock_job_svc_cls, mock_get_db, mock_db_context):
    mock_get_db.return_value = mock_db_context[0]
    
    job_svc_instance = mock_job_svc_cls.return_value
    pipeline_instance = mock_pipeline_cls.return_value
    
    job_mock = MagicMock(status="QUEUED")
    job_svc_instance.get_job = AsyncMock(return_value=job_mock)
    job_svc_instance.update_job = AsyncMock()
    pipeline_instance.execute_pipeline = AsyncMock(return_value={"status": "done"})

    # Run the synchronous Celery task
    result = generate_ai_artifacts_task("job-123", str(uuid.uuid4()), str(uuid.uuid4()))
    
    assert result["status"] == "completed"
    assert result["result"] == {"status": "done"}
    assert job_svc_instance.update_job.call_count == 1
