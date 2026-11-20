# Phase 6 — Validation and release checklist

## Automated checks run for this phase

- `python -m pytest -q`: **19 passed**.
- `python -m compileall -q app dashboard tests`: passed.
- Secret-file scan for `.env`, private-key, and local database files in the packaged project: no matches.

## Checks not run in this environment

Docker is not installed in the execution environment, so `docker compose config`, image builds, and container startup could not be verified. The following require the developer's configured environment and credentials:

- PostgreSQL/Alembic migration against a real database.
- API and Streamlit end-to-end flow with the local Docker Compose stack.
- Gemini integration with a valid API key and live provider response.
- Celery/Redis worker execution and Langfuse delivery.
- Browser-level responsive/accessibility checks.

## Local release gate

From the project root:

```bash
python -m pytest -q
python -m compileall -q app dashboard tests
docker compose config
docker compose up --build
```

Then verify registration/login, workout logging, recovery entry, analytics/insights, and dashboard navigation in the running application. Confirm `.env` is local and never included in the release archive.

## Scope

Passing the automated tests establishes the tested code paths only. It does not certify production security, database migration safety, provider availability, or deployment readiness. Review environment secrets, CORS, database backups, and deployment-specific settings before production use.
