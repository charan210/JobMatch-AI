from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO



class BaseParser(ABC):
    """
    Abstract base class for all document parsers.
    Parsers are responsible solely for extracting text from documents.
    They must not contain business logic or database operations.
    """

    @abstractmethod
    def parse(self, file_obj: BinaryIO) -> str:
        """
        Extract text from the given file object.

        Args:
            file_obj (BinaryIO): The file-like object to parse.

        Returns:
            str: The extracted text.

        Raises:
            ParserError: If the document is corrupted or cannot be parsed.
        """
        pass
