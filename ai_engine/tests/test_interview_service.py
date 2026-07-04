import pytest
from unittest.mock import AsyncMock, patch

from app.core.gemini_client import GeminiClientException
from ai_engine.interview_generation.interview_service import InterviewQuestionService

@pytest.fixture
def mock_gemini_client():
    return AsyncMock()


@pytest.fixture
def interview_service(mock_gemini_client):
    return InterviewQuestionService(gemini_client=mock_gemini_client)


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
async def test_generate_questions_success(interview_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.return_value = {
        "questions": [
            {
                "question": "What is dependency injection in FastAPI?",
                "category": "Technical",
                "difficulty": "Medium",
                "expected_skill": "FastAPI"
            }
        ]
    }

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is False
    assert len(result.questions) == 1
    assert result.questions[0].difficulty == "Medium"


@pytest.mark.asyncio
async def test_generate_questions_invalid_difficulty(interview_service, mock_gemini_client, sample_profiles):
    # 'Expert' is not a valid literal
    mock_gemini_client.generate_json.return_value = {
        "questions": [
            {
                "question": "What is FastAPI?",
                "category": "Technical",
                "difficulty": "Expert",
                "expected_skill": "FastAPI"
            }
        ]
    }

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True
    assert len(result.questions) > 0


@pytest.mark.asyncio
async def test_generate_questions_missing_fields(interview_service, mock_gemini_client, sample_profiles):
    # Missing expected_skill
    mock_gemini_client.generate_json.return_value = {
        "questions": [
            {
                "question": "What is FastAPI?",
                "category": "Technical",
                "difficulty": "Medium"
            }
        ]
    }

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True


@pytest.mark.asyncio
async def test_generate_questions_gemini_exception(interview_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.side_effect = GeminiClientException("Timeout")

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True


@pytest.mark.asyncio
async def test_generate_questions_prompt_load_error(interview_service, mock_gemini_client, sample_profiles):
    with patch("ai_engine.interview_generation.interview_service._load_interview_prompt_template", side_effect=Exception("Disk error")):
        result = await interview_service.generate_questions(
            sample_profiles["candidate"],
            sample_profiles["job"],
            sample_profiles["skill_gap"]
        )

    assert result.is_fallback is True


@pytest.mark.asyncio
async def test_generate_questions_empty_dict(interview_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.return_value = {}

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True


@pytest.mark.asyncio
async def test_generate_questions_none(interview_service, mock_gemini_client, sample_profiles):
    mock_gemini_client.generate_json.return_value = None

    result = await interview_service.generate_questions(
        sample_profiles["candidate"],
        sample_profiles["job"],
        sample_profiles["skill_gap"]
    )

    assert result.is_fallback is True


@pytest.mark.asyncio
async def test_fallback_json_loading_failure(interview_service, mock_gemini_client, sample_profiles):
    # Test that if the JSON file itself is broken/missing, the hardcoded fail-safe works
    mock_gemini_client.generate_json.return_value = None
    from ai_engine.interview_generation.interview_service import _load_fallback_questions
    _load_fallback_questions.cache_clear()
    
    with patch("ai_engine.interview_generation.interview_service.json.load", side_effect=Exception("Bad JSON")):
        result = await interview_service.generate_questions(
            sample_profiles["candidate"],
            sample_profiles["job"],
            sample_profiles["skill_gap"]
        )
    
    assert result.is_fallback is True
    assert len(result.questions) == 1
    assert result.questions[0].question == "Can you describe your experience with the required skills?"
