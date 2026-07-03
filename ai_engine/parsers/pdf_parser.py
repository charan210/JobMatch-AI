from __future__ import annotations

from typing import BinaryIO

from pypdf import PdfReader

from ai_engine.exceptions import ParserError
from ai_engine.parsers.base_parser import BaseParser


class PdfParser(BaseParser):
    """
    Parser for PDF documents.
    """

    def parse(self, file_obj: BinaryIO) -> str:
        try:
            reader = PdfReader(file_obj)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            raise ParserError(f"Failed to parse PDF document: {str(e)}") from e
