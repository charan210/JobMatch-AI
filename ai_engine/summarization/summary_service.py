from __future__ import annotations

import os
from functools import lru_cache
from pydantic import ValidationError
from typing import Any

from app.core.gemini_client import GeminiClient, GeminiClientException
from app.schemas.ai_schemas import AISummaryBase
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_summary_prompt_template() -> str:
    """Reads the prompt template from disk and caches it in memory."""
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "prompts",
        "summary_v1.txt",
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


class SummaryService:
    """
    Service to orchestrate Gemini API generation for Candidate Summaries.
    Follows strict failure handling to produce a deterministic fallback.
    """

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self.client = gemini_client or GeminiClient()

    def _load_prompt(self, **kwargs: Any) -> str:
        try:
            template = _load_summary_prompt_template()
            return template.format(**kwargs)
        except Exception as exc:
            # Trigger the fallback gracefully
            logger.error("prompt_load_failed", error_type="prompt_load_error")
            raise GeminiClientException("Failed to load or format prompt.") from exc

    def _generate_fallback(self) -> AISummaryBase:
        return AISummaryBase(
            strengths=[],
            weaknesses=[],
            recommendation="Consider",
            summary_text="Automated summary could not be generated. Please review the candidate's profile manually.",
            is_fallback=True,
        )

    async def generate_summary(
        self,
        candidate_profile: dict[str, Any],
        job_profile: dict[str, Any],
        skill_gap_result: dict[str, Any]
    ) -> AISummaryBase:
        """
        Generates the AI Summary for a candidate, catching all exceptions to return a fallback.
        """
        candidate_id = candidate_profile.get("id")
        job_id = job_profile.get("id")
        logger.info("ai_summary_started", candidate_id=candidate_id, job_id=job_id)
        
        try:
            # Format placeholder parameters
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
            
            response_schema = AISummaryBase.model_json_schema()
            
            raw_json = await self.client.generate_json(
                prompt=prompt,
                response_schema=response_schema
            )
            
            if not isinstance(raw_json, dict):
                raise ValueError("Gemini client returned non-dictionary output")

            # Validate with Pydantic and safely update immutable fallback flag
            validated = AISummaryBase.model_validate(raw_json)
            validated = validated.model_copy(update={"is_fallback": False})
            
            logger.info("ai_summary_completed", candidate_id=candidate_id, job_id=job_id)
            return validated

        except ValidationError:
            logger.warning("ai_summary_failed", error_type="validation_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
        except GeminiClientException:
            logger.warning("ai_summary_failed", error_type="provider_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
        except Exception:
            # Catch everything else to guarantee no unhandled exceptions bubble up
            logger.error("ai_summary_failed", error_type="unexpected_error", candidate_id=candidate_id, job_id=job_id)
            return self._generate_fallback()
