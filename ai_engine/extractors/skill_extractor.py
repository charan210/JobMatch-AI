from __future__ import annotations

import json
import os
import re

from ai_engine.exceptions import ExtractorError
from ai_engine.extractors.base_extractor import BaseExtractor


class SkillExtractor(BaseExtractor):
    """
    Extracts technical skills from text based on a predefined dictionary.
    """

    def __init__(self, master_skills_path: str | None = None) -> None:
        if master_skills_path is None:
            # Default to the skills_master.json in the same directory
            master_skills_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "skills_master.json"
            )
        self.master_skills = self._load_skills(master_skills_path)
        # Precompile regex for faster exact word matching
        self._compiled_skills = {
            skill: re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
            for skill in self.master_skills
        }

    def _load_skills(self, path: str) -> list[str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ExtractorError(f"Failed to load skills from {path}: {str(e)}") from e

    def extract(self, text: str) -> list[str]:
        """
        Extracts matched skills from the text.
        Returns a deduplicated list of standard skill names.
        """
        try:
            extracted = set()
            for skill, pattern in self._compiled_skills.items():
                if pattern.search(text):
                    extracted.add(skill)
            return sorted(list(extracted))
        except Exception as e:
            raise ExtractorError(f"Skill extraction failed: {str(e)}") from e
