# Phase 4 — Background jobs and observability

## Included

- Optional Celery worker configured with Redis broker/backend.
- A worker health task that can verify the queue path without reading user data.
- Optional Langfuse tracing helper. It is a no-op unless both keys are configured and does not attach workout content or credentials.
- Docker Compose services for Redis and the worker.

## Verify the worker

With Docker Compose running, execute:

```bash
docker compose exec worker celery -A app.jobs.celery_app:celery_app call repsense.jobs.worker_health
```

Then inspect worker logs for task completion. This phase does not yet move insight generation into the queue; the existing API analysis remains synchronous and functional without Redis.

## Configuration

Set `REDIS_URL` and, optionally, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` in `.env`. Keep secrets out of source control. Langfuse is optional.
