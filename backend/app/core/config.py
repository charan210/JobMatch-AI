from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Any, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration sourced entirely from environment variables
    or the .env file. Pydantic validates types and raises on startup if required
    fields are missing or malformed — fail fast, never silently misconfigure.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Recruitment Automation System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(
        default="development",
        pattern="^(development|staging|production)$",
    )
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Vite dev server default port — aligns with React + Vite frontend stack
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Database — PostgreSQL only (localhost for Day 2) ──────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:12345678@localhost:5433/aras_db"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=5, le=120)
    DATABASE_ECHO: bool = False

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Synchronous DSN required by Alembic migrations.
        Replaces asyncpg driver with psycopg2 for sync operations only.
        """
        url = self.DATABASE_URL
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        url = url.replace("postgresql://", "postgresql+psycopg2://")
        return url

    # ── Security (structure in place for Sprint 2 auth implementation) ─────────
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    LOG_FORMAT: str = Field(
        default="console",
        pattern="^(console|json)$",
    )

    # ── Embeddings / Ranking (Sprint 5 Phase 2) ─────────────────────────────
    # Choose embedding backend: 'stub' (ai_engine) or 'sentence_transformers'
    EMBEDDING_BACKEND: str = Field(default="stub")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")

    # Ranking component weights (must sum to <= 1.0; remaining weight treated as reserved/AI fallback)
    RANK_WEIGHT_SEMANTIC: float = Field(default=0.35)
    RANK_WEIGHT_SKILL: float = Field(default=0.25)
    RANK_WEIGHT_EXPERIENCE: float = Field(default=0.20)
    RANK_WEIGHT_EDUCATION: float = Field(default=0.10)
    RANK_WEIGHT_AI: float = Field(default=0.10)
    
    # Celery / Redis broker for async jobs
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")

    # ── AI Engine (Milestone 2) ────────────────────────────────────────────────
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")

    # ── Storage (Milestone 1) ───────────────────────────────────────────────────
    STORAGE_BACKEND: str = Field(default="local", pattern="^(local|s3)$")
    LOCAL_STORAGE_DIR: str = Field(default="uploads")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached singleton Settings instance.

    Use as a FastAPI dependency injected into routes:
        from app.core.config import get_settings
        settings: Settings = Depends(get_settings)

    Or import the module-level singleton for non-DI usage:
        from app.core.config import settings
    """
    return Settings()


# Module-level singleton — used by db/database.py and core/logging.py
# which are imported before the FastAPI DI container is available.
settings: Settings = get_settings()