from __future__ import annotations


class AIEngineError(Exception):
    """Base exception for all AI Engine errors."""
    pass


class ParserError(AIEngineError):
    """Raised when a file cannot be parsed."""
    pass


class ExtractorError(AIEngineError):
    """Raised when extraction fails."""
    pass
