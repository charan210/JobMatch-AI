from __future__ import annotations


from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from celery import Celery

    celery_app: Celery = Celery(
        "app.tasks",
        broker=settings.CELERY_BROKER_URL,
        include=["app.tasks.tasks"]
    )
    # Basic configuration; individual tasks may set retries/timeouts
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.task_ignore_result = False
    logger.info("celery_app_initialized", broker=settings.CELERY_BROKER_URL)
except Exception as exc:  # Celery may not be installed in dev/test env
    celery_app = None  # type: ignore
    logger.warning("celery_not_available", error=str(exc))
