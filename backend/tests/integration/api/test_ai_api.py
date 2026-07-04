import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.fixture
def sample_uuids():
    return {
        "candidate_id": str(uuid.uuid4()),
        "job_id": str(uuid.uuid4()),
        "job_task_id": "job-123"
    }

@pytest.mark.asyncio
@patch("app.api.v1.ai.CandidateService.get_candidate")
@patch("app.api.v1.ai.JobService.get_job")
@patch("app.api.v1.ai.AIPipelineService.check_idempotency")
@patch("app.api.v1.ai.AsyncJobService.create_job")
@patch("app.tasks.tasks.generate_ai_artifacts_task.delay")
async def test_generate_success(
    mock_delay, mock_create_job, mock_check_idempotency, mock_get_job, mock_get_candidate,
    client: AsyncClient, auth_header: dict[str, str], sample_uuids
):
    mock_get_candidate.return_value = True
    mock_get_job.return_value = True
    mock_check_idempotency.return_value = None
    
    class MockJob:
        id = sample_uuids["job_task_id"]
        status = "QUEUED"
        
    mock_create_job.return_value = MockJob()
    
    response = await client.post(
        "/api/v1/ai/generate",
        json={"candidate_id": sample_uuids["candidate_id"], "job_id": sample_uuids["job_id"]},
        headers=auth_header
    )
    assert response.status_code == 202
    assert response.json()["job_id"] == sample_uuids["job_task_id"]
    assert response.json()["status"] == "QUEUED"
    assert response.json()["status_url"] == f"/api/v1/ai/jobs/{sample_uuids['job_task_id']}"
    mock_delay.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.v1.ai.CandidateService.get_candidate")
@patch("app.api.v1.ai.JobService.get_job")
@patch("app.api.v1.ai.AIPipelineService.check_idempotency")
@patch("app.tasks.tasks.generate_ai_artifacts_task.delay")
async def test_generate_already_running(
    mock_delay, mock_check_idempotency, mock_get_job, mock_get_candidate,
    client: AsyncClient, auth_header: dict[str, str], sample_uuids
):
    mock_get_candidate.return_value = True
    mock_get_job.return_value = True
    mock_check_idempotency.return_value = {"status": "STARTED", "job_id": sample_uuids["job_task_id"]}
    
    response = await client.post(
        "/api/v1/ai/generate",
        json={"candidate_id": sample_uuids["candidate_id"], "job_id": sample_uuids["job_id"]},
        headers=auth_header
    )
    assert response.status_code == 202
    assert response.json()["status"] == "STARTED"
    mock_delay.assert_not_called()

@pytest.mark.asyncio
@patch("app.api.v1.ai.CandidateService.get_candidate")
@patch("app.api.v1.ai.JobService.get_job")
@patch("app.api.v1.ai.AIPipelineService.check_idempotency")
@patch("app.tasks.tasks.generate_ai_artifacts_task.delay")
async def test_generate_already_completed(
    mock_delay, mock_check_idempotency, mock_get_job, mock_get_candidate,
    client: AsyncClient, auth_header: dict[str, str], sample_uuids
):
    mock_get_candidate.return_value = True
    mock_get_job.return_value = True
    mock_check_idempotency.return_value = {"status": "COMPLETED", "job_id": sample_uuids["job_task_id"]}
    
    response = await client.post(
        "/api/v1/ai/generate",
        json={"candidate_id": sample_uuids["candidate_id"], "job_id": sample_uuids["job_id"]},
        headers=auth_header
    )
    assert response.status_code == 202
    assert response.json()["status"] == "COMPLETED"
    mock_delay.assert_not_called()

@pytest.mark.asyncio
@patch("app.api.v1.ai.CandidateService.get_candidate")
async def test_generate_missing_candidate(
    mock_get_candidate, client: AsyncClient, auth_header: dict[str, str], sample_uuids
):
    mock_get_candidate.return_value = None
    
    response = await client.post(
        "/api/v1/ai/generate",
        json={"candidate_id": sample_uuids["candidate_id"], "job_id": sample_uuids["job_id"]},
        headers=auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_generate_unauthorized(client: AsyncClient, sample_uuids):
    response = await client.post(
        "/api/v1/ai/generate",
        json={"candidate_id": sample_uuids["candidate_id"], "job_id": sample_uuids["job_id"]}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
@patch("app.api.v1.ai.AIPipelineService.get_skill_gap")
async def test_get_skill_gap(mock_get_skill_gap, client: AsyncClient, auth_header: dict[str, str], sample_uuids):
    mock_get_skill_gap.return_value = {
        "matching_skills": ["Python"],
        "missing_skills": ["Docker"],
        "match_percentage": 50.0
    }
    
    response = await client.get(
        f"/api/v1/ai/skill-gap/{sample_uuids['candidate_id']}/{sample_uuids['job_id']}",
        headers=auth_header
    )
    assert response.status_code == 200
    assert response.json()["match_percentage"] == 50.0
