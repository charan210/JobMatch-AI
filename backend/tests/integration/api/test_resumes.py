import io
import pytest
from httpx import AsyncClient
from typing import Any
import uuid

@pytest.mark.asyncio
async def test_upload_resume_success(client: AsyncClient, async_session: Any) -> None:
    candidate_id = uuid.uuid4()
    
    # Create a candidate in the real db session
    from app.models.candidate import Candidate
    candidate = Candidate(id=str(candidate_id), full_name="Test Candidate")
    async_session.add(candidate)
    await async_session.commit()
    
    file_content = b"fake pdf content"
    files = {"file": ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"candidate_id": str(candidate_id)}
    
    response = await client.post("/resumes/upload", data=data, files=files)
    assert response.status_code == 202
    result = response.json()
    assert result["status"] == "uploaded"
    assert "resume_id" in result

@pytest.mark.asyncio
async def test_upload_resume_invalid_mime_type(client: AsyncClient) -> None:
    candidate_id = uuid.uuid4()
    file_content = b"fake text content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    data = {"candidate_id": str(candidate_id)}
    
    response = await client.post("/resumes/upload", data=data, files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["message"]

@pytest.mark.asyncio
async def test_upload_resume_file_too_large(client: AsyncClient, monkeypatch) -> None:
    import app.api.v1.resumes as resumes_module
    monkeypatch.setattr(resumes_module, "MAX_FILE_SIZE", 10) # 10 bytes limit
    
    candidate_id = uuid.uuid4()
    file_content = b"this content is way larger than 10 bytes"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"candidate_id": str(candidate_id)}
    
    response = await client.post("/resumes/upload", data=data, files=files)
    assert response.status_code == 400
    assert "File size exceeds maximum" in response.json()["message"]
