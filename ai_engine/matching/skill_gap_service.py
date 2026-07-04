from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillGapResult:
    matching_skills: list[str]
    missing_skills: list[str]
    match_percentage: float


class SkillGapService:
    """
    Deterministic engine to compute the gap between candidate skills and required job skills.
    This component does not rely on LLMs or external services.
    """

    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill for comparison by stripping whitespace and lowercasing."""
        return skill.strip().lower()

    def analyze(self, candidate_skills: list[str], required_job_skills: list[str]) -> SkillGapResult:
        """
        Analyzes the gap between candidate skills and required job skills.
        Performs case-insensitive deterministic set differences.
        """
        normalized_required = {self._normalize_skill(s) for s in required_job_skills if s.strip()}
        normalized_candidate = {self._normalize_skill(s) for s in candidate_skills if s.strip()}

        if not normalized_required:
            return SkillGapResult(
                matching_skills=[],
                missing_skills=[],
                match_percentage=100.0,
            )

        matching = normalized_required.intersection(normalized_candidate)

        match_percentage = round((len(matching) / len(normalized_required)) * 100.0, 2)

        # Preserve original order of required skills
        matching_ordered = []
        missing_ordered = []
        seen = set()

        for skill in required_job_skills:
            if not skill.strip():
                continue
            norm_skill = self._normalize_skill(skill)
            if norm_skill in seen:
                continue
            seen.add(norm_skill)

            if norm_skill in matching:
                matching_ordered.append(skill.strip())
            else:
                missing_ordered.append(skill.strip())

        return SkillGapResult(
            matching_skills=matching_ordered,
            missing_skills=missing_ordered,
            match_percentage=match_percentage,
        )
