from __future__ import annotations

import re
from typing import Any

from ai_engine.exceptions import ExtractorError
from ai_engine.extractors.base_extractor import BaseExtractor


class ContactExtractor(BaseExtractor):
    """
    Extracts contact information (email, phone, LinkedIn) from text using Regex.
    """

    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_REGEX = r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    LINKEDIN_REGEX = r"linkedin\.com/in/[a-zA-Z0-9_-]+"

    def extract(self, text: str) -> dict[str, Any]:
        try:
            email_match = re.search(self.EMAIL_REGEX, text)
            phone_match = re.search(self.PHONE_REGEX, text)
            linkedin_match = re.search(self.LINKEDIN_REGEX, text, re.IGNORECASE)

            # Simple heuristic for name: assume it's one of the first few non-empty lines
            name = None
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if lines:
                # Often the first line is the name
                name = lines[0]

            # In a real NLP implementation, you'd use NER. Here we use deterministic fallback.
            return {
                "name": name,
                "email": email_match.group(0) if email_match else None,
                "phone": phone_match.group(0).strip() if phone_match else None,
                "linkedin": linkedin_match.group(0) if linkedin_match else None,
            }
        except Exception as e:
            raise ExtractorError(f"Contact extraction failed: {str(e)}") from e
