from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any



class BaseExtractor(ABC):
    """
    Abstract base class for all text extractors.
    Extractors pull structured data from raw text strings.
    """

    @abstractmethod
    def extract(self, text: str) -> dict[str, Any] | list[Any] | Any:
        """
        Extract specific information from the provided text.

        Args:
            text (str): The raw text to process.

        Returns:
            The extracted data structure.

        Raises:
            ExtractorError: If extraction fails due to an internal error.
        """
        pass
