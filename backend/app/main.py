from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.database import check_database_connection, close_database_connections

logger = get_logger(__name__)


# ── Application Lifespan ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    STARTUP sequence:
      1. configure_logging()         — structured logging active before anything else
      2. Log configuration summary   — safe values only, no secrets or PII
      3. check_database_connection() — fail fast if PostgreSQL unreachable
      4. yield                       — application is ready to serve requests

    SHUTDOWN sequence:
      1. close_database_connections() — return all pooled connections gracefully
      2. Log shutdown event
    """
    # ── STARTUP ────────────────────────────────────────────────────────────────
    configure_logging()

    logger.info(
        "aras_starting",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
        debug=settings.DEBUG,
    )

    await check_database_connection()

    logger.info("aras_ready", message="ARAS API is ready to accept requests.")

    yield  # ── Application is live ────────────────────────────────────────────

    # ── SHUTDOWN ───────────────────────────────────────────────────────────────
    await close_database_connections()
    logger.info("aras_shutdown", message="ARAS API shutdown complete.")
    # Note: Celery workers run in separate processes; no in-process worker to stop.


# ── Application Factory ────────────────────────────────────────────────────────

def create_application() -> FastAPI:
    """
    Constructs and returns the configured FastAPI application instance.

    Separated from module-level instantiation so tests can call
    create_application() to get a fresh, fully configured app without
    triggering the lifespan startup sequence.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI Recruitment Automation System (ARAS) — "
            "Automates resume screening, candidate evaluation, ranking, "
            "skill gap analysis, and interview question generation."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Allows React + Vite frontend (localhost:5173) to call the API.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # ── Exception Handlers ─────────────────────────────────────────────────────
    register_exception_handlers(application)

    # ── Routers ────────────────────────────────────────────────────────────────
    _register_routers(application)

    return application


def _register_routers(application: FastAPI) -> None:
    """
    Central router registry.

    Day 2 registers:
      health.py → GET /,  GET /health,  GET /api/v1/health/detailed

    Future sprint additions (do NOT add these today):
      Sprint 2: auth_router, users_router
      Sprint 3: resumes_router
      Sprint 4: candidates_router
      Sprint 5: rankings_router
      Sprint 6: ai_router (summaries, skill-gap, interview questions)
      Sprint 7: analytics_router, reports_router
    """
    from app.api.v1.health import router as health_router
    from app.api.v1.jobs import router as jobs_router
    from app.api.v1.jobs_status import router as jobs_status_router
    from app.api.v1.candidates import router as candidates_router
    from app.api.v1.resumes import router as resumes_router
    from app.api.v1.rankings import router as rankings_router
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.api.v1.ai import router as ai_router

    application.include_router(health_router)
    application.include_router(jobs_router)
    application.include_router(jobs_status_router)
    application.include_router(candidates_router)
    application.include_router(resumes_router)
    application.include_router(rankings_router)
    application.include_router(auth_router)
    application.include_router(users_router)
    application.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Generation"])


# ── Module-Level App Instance ──────────────────────────────────────────────────
# Uvicorn uses this: uvicorn app.main:app
app: FastAPI = create_application()