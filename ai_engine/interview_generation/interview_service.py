from __future__ import annotations

import os
import json
from functools import lru_cache
from pydantic import ValidationError, BaseModel
from typing import Any

from app.core.gemini_client import GeminiClient, GeminiClientException
from app.schemas.ai_schemas import InterviewQuestionResponse, InterviewQuestion
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_interview_prompt_template() -> str:
    """Reads the prompt template from disk and caches it in memory."""
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "prompts",
        "question_v1.txt",
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


@lru_cache(maxsize=1)
def _load_fallback_questions() -> InterviewQuestionResponse:
    """Loads fallback questions from the static JSON file."""
    fallback_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fallback_questions.json",
    )
    try:
        with open(fallback_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return InterviewQuestionResponse.model_validate(data)
    except Exception:
        logger.error("fallback_load_failed", error_type="fallback_load_error")
        # Hardcoded fail-safe if the fallback JSON itself is broken
        return InterviewQuestionResponse(
            questions=[
                InterviewQuestion(
                    question="Can you describe your experience with the required skills?",
                    category="Technical",
                    difficulty="Medium",
                    expected_skill="General"
                )
            ],
            is_fallback=True
        )


class InterviewQuestionService:
    """
    Service to orchestrate Gemini API generation for Interview Questions.
    Follows strict failure handling to produce a deterministic fallback.
    """

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self.client = gemini_client or GeminiClient()

    def _load_prompt(self, **kwargs: Any) -> str:
        try:
            template = _load_interview_prompt_template()
            return template.format(**kwargs)
        except Exception as exc:
            logger.error("prompt_load_failed", error_type="prompt_load_error")
            raise GeminiClientException("Failed to load or format prompt.") from exc

    def _generate_fallback(self) -> InterviewQuestionResponse:
        return _load_fallback_questions().model_copy(deep=True)

    async def generate_questions(
        self,
        candidate_profile: dict[str, Any],
        job_profile: dict[str, Any],
        skill_gap_result: dict[str, Any]
    ) -> InterviewQuestionResponse:
        """
        Generates Interview Questions, catching all exceptions to return a fallback.
        """
        candidate_id = candidate_profile.get("id")
        job_id = job_profile.get("id")
        logger.info("interview_generation_started", candidate_id=candidate_id, job_id=job_id)
        
        try:
            prompt = self._load_prompt(
                experience_years=candidate_profile.get("experience_years", "Unknown"),
                education=candidate_profile.get("education", "Unknown"),
                candidate_skills=", ".join(candidate_profile.get("skills", [])),
                job_title=job_profile.get("title", "Unknown"),
                required_experience=job_profile.get("experience_required", "Unknown"),
                required_education=job_profile.get("education_required", "Unknown"),
                required_skills=", ".join(job_profile.get("skills", [])),
                matching_skills=", ".join(skill_gap_result.get("matching_skills", [])),
                missing_skills=", ".join(skill_gap_result.get("missing_skills", [])),
            )
            
            class GeminiInterviewQuestionResponse(BaseModel):
                questions: list[InterviewQuestion]

            response_schema = GeminiInterviewQuestionResponse.model_json_schema()
            
            raw_json = await self.client.generate_json(
                prompt=prompt,
                response_schema=response_schema
            )
            
            if not isinstance(raw_json, dict):
                raise ValueError("Gemini client returned non-dictionary output")

            # Map the parsed JSON back into our actual application schema 
            # We use the Gemini schema to strictly validate what Gemini returned
            gemini_validated = GeminiInterviewQuestionResponse.model_validate(raw_json)
            validated = InterviewQuestionResponse(questions=gemini_validated.questions, is_fallback=False)
            
            logger.info("interview_generation_completed", candidate_id=candidate_id, job_id=job_id)
            return validated

        except ValidationError:
            logger.warning("interview_generation_failed", error_type="validation_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
        except GeminiClientException:
            logger.warning("interview_generation_failed", error_type="provider_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
        except Exception:
            # Catch everything else to guarantee no unhandled exceptions bubble up
            logger.error("interview_generation_failed", error_type="unexpected_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
