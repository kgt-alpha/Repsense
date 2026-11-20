"""Celery application; API operation remains available without a worker."""
from celery import Celery

from app.config import get_settings

settings = get_settings()
celery_app = Celery(
    "repsense",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.jobs.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=300,
    result_expires=3600,
)
