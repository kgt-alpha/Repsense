# Code Standards

## Python
- Target a consistent supported Python version and pin compatible dependencies.
- Use type hints for public functions and API schemas.
- Keep functions small and names explicit.
- Prefer pure functions for calculations.
- Avoid hidden global state and broad exception swallowing.
- Use timezone-aware datetimes and a documented storage convention (prefer UTC in persistence).
- Keep formatting/linting choices consistent with the repository.

## Validation
- Reject negative reps, invalid loads, malformed timestamps, and impossible indexes.
- Define allowed units and conversion behavior.
- Set reasonable bounds for text lengths and list sizes.
- Missing values must remain missing; never silently convert them to zero.
- Validate Gemini output against a Pydantic model.

## Database
- Use SQLAlchemy sessions with clear lifecycle management.
- Use Alembic migrations for schema changes.
- Add constraints and indexes where useful.
- Avoid N+1 queries on workout histories.
- Do not store API keys or credentials in the database without a justified secure design.

## API
- Keep route handlers thin.
- Return appropriate status codes and stable response shapes.
- Do not expose stack traces or internal secrets to clients.
- Add pagination to potentially unbounded lists.
- Use idempotency or duplicate prevention where the workflow needs it.

## Tests
- Test normal cases, boundaries, missing history, invalid inputs, zero variance, and empty results.
- Freeze dates or inject a clock when testing time-dependent rules.
- Mock Gemini in unit tests; do not require a real API key for the test suite.
- Keep integration tests explicit about whether PostgreSQL is required.
- Report exactly which commands were run and whether they passed.
