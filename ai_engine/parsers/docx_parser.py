from __future__ import annotations

from typing import BinaryIO

import docx

from ai_engine.exceptions import ParserError
from ai_engine.parsers.base_parser import BaseParser


class DocxParser(BaseParser):
    """
    Parser for DOCX documents.
    """

    def parse(self, file_obj: BinaryIO) -> str:
        try:
            document = docx.Document(file_obj)
            text_parts = []
            for paragraph in document.paragraphs:
                if paragraph.text:
                    text_parts.append(paragraph.text)
            return "\n".join(text_parts)
        except Exception as e:
            raise ParserError(f"Failed to parse DOCX document: {str(e)}") from e
