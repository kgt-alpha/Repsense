"""Small operational tasks used to verify the optional worker pipeline."""
from datetime import datetime, timezone

from app.jobs.celery_app import celery_app
from app.observability import trace_operation


@celery_app.task(name="repsense.jobs.worker_health")
def worker_health() -> dict[str, str]:
    """Return a timestamped worker response without touching user data."""
    with trace_operation("worker.health"):
        return {"status": "ok", "checked_at": datetime.now(timezone.utc).isoformat()}
