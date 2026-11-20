# Development Guide

## Local setup

1. Use Python 3.12 and create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a unique `JWT_SECRET_KEY`.
4. Start PostgreSQL with `docker compose up -d db`.
5. Apply migrations using `alembic upgrade head`.
6. Run the API with `uvicorn app.main:app --reload`.
7. Run the dashboard separately with `streamlit run dashboard/Home.py`.

## Verification

Run `python -m pytest -v`. API tests use isolated SQLite unless a test explicitly documents another database. PostgreSQL migrations, Docker startup, and live Gemini behavior require separate verification.

## Current six-phase plan

1. Repository baseline and architecture alignment.
2. Core backend integrity and analytics correctness.
3. Evidence-grounded Gemini explanations and controlled query support.
4. Background processing and observability.
5. Dashboard usability and complete user workflows.
6. Testing, security review, Docker and release readiness.

Update `docs/progress-tracker.md` with verified work, actual test commands/results, remaining risks, and next steps.
