from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Custom Application Exceptions ─────────────────────────────────────────────

class ARASBaseException(Exception):
    """Base for all ARAS domain exceptions. Never raise this directly."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors: List[Dict[str, Any]] = errors or []
        super().__init__(message)


class NotFoundError(ARASBaseException):
    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            message=f"{resource} '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(ARASBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ValidationError(ARASBaseException):
    def __init__(
        self,
        message: str,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors or [],
        )


class DatabaseError(ARASBaseException):
    def __init__(self, message: str = "A database error occurred.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ── JSON Error Envelope Builder ───────────────────────────────────────────────

def _error_response(
    status_code: int,
    message: str,
    errors: Optional[List[Any]] = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": errors or [],
        },
    )


# ── Global Exception Handlers ──────────────────────────────────────────────────

async def _handle_aras_exception(
    request: Request,
    exc: Any,
) -> Response:
    logger.warning(
        "aras_exception",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        message=exc.message,
    )
    return _error_response(exc.status_code, exc.message, exc.errors)


async def _handle_http_exception(
    request: Request,
    exc: Any,
) -> Response:
    logger.warning(
        "http_exception",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=str(exc.detail),
    )
    return _error_response(exc.status_code, str(exc.detail))


async def _handle_validation_exception(
    request: Request,
    exc: Any,
) -> Response:
    errors = [
        {
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    logger.info(
        "request_validation_failed",
        path=request.url.path,
        method=request.method,
        error_count=len(errors),
    )
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Request validation failed.",
        errors,
    )


async def _handle_unhandled_exception(
    request: Request,
    exc: Exception,
) -> Response:
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "An unexpected server error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers all global exception handlers on the FastAPI application.
    Called once from main.py create_application().
    """
    app.add_exception_handler(ARASBaseException, _handle_aras_exception)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(HTTPException, _handle_http_exception)
    app.add_exception_handler(RequestValidationError, _handle_validation_exception)
    app.add_exception_handler(Exception, _handle_unhandled_exception)