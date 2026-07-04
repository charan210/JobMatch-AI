import pytest
from unittest.mock import AsyncMock, patch

from app.core.gemini_client import GeminiClientException
from ai_engine.summarization.summary_service import SummaryService

@pytest.fixture
def mock_gemini_client():
    client = AsyncMock()
    return client


@pytest.fixture
def summary_service(mock_gemini_client):
    return SummaryService(gemini_client=mock_gemini_client)


@pytest.fixture
def sample_profiles():
    return {
        "candidate": {
            "id": "123",
            "experience_years": 5,
            "education": "BS Computer Science",
            "skills": ["Python", "Docker"]
        },
        "job": {
            "id": "456",
            "title": "Backend Engineer",
            "experience_required": 3,
            "education_required": "BS",
            "skills": ["Python", "FastAPI"]
        },
        "skill_gap": {
            "matching_skills": ["Python"],
            "missing_skills": ["FastAPI"]
        }
    }


@pytest.mark.asyncio
async def test_generate_summary_success(summary_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.return_value = {
        "strengths": ["Strong Python experience"],
        "weaknesses": ["Missing FastAPI"],
        "recommendation": "Recommended",
        "summary_text": "Good fit overall."
    }

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is False
    assert result.recommendation == "Recommended"
    assert result.strengths == ["Strong Python experience"]
    assert mock_gemini_client.generate_json.called


@pytest.mark.asyncio
async def test_generate_summary_invalid_schema(summary_service, mock_gemini_client, sample_profiles):
    # Returning invalid recommendation literal
    mock_gemini_client.generate_json.return_value = {
        "strengths": ["Strong Python"],
        "weaknesses": [],
        "recommendation": "Maybe",
        "summary_text": "Not sure."
    }

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"


@pytest.mark.asyncio
async def test_generate_summary_missing_fields(summary_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.return_value = {
        "strengths": ["Strong Python"],
        "recommendation": "Recommended"
        # missing weaknesses, summary_text
    }

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"


@pytest.mark.asyncio
async def test_generate_summary_gemini_exception(summary_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.side_effect = GeminiClientException("API Timeout")

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"


@pytest.mark.asyncio
async def test_generate_summary_prompt_load_error(summary_service, mock_gemini_client, sample_profiles):
    # Notice we mock the caching function so we bypass disk load
    with patch("ai_engine.summarization.summary_service._load_summary_prompt_template", side_effect=Exception("Disk failure")):
        result = await summary_service.generate_summary(
            sample_profiles["candidate"],
            sample_profiles["job"],
            sample_profiles["skill_gap"]
        )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"


@pytest.mark.asyncio
async def test_generate_summary_empty_dict(summary_service, mock_gemini_client, sample_profiles):
    # Test realistic provider failure where response is empty JSON object
    mock_gemini_client.generate_json.return_value = {}

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"


@pytest.mark.asyncio
async def test_generate_summary_none(summary_service, mock_gemini_client, sample_profiles):
    # Test realistic provider failure where response is None
    mock_gemini_client.generate_json.return_value = None

    result = await summary_service.generate_summary(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert result.recommendation == "Consider"
