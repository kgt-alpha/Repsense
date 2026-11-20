# Architecture

## Stack
- API: FastAPI
- Schemas/validation: Pydantic
- Persistence: PostgreSQL + SQLAlchemy
- Migrations: Alembic
- UI: Streamlit
- Local orchestration: Docker Compose
- Tests: pytest
- LLM: Gemini API, isolated behind a service
- Redis: optional; introduce only for a real queue/cache need

## Dependency direction
`Streamlit UI → FastAPI routes → application/services → repositories → SQLAlchemy/PostgreSQL`

Analytics and evidence construction should be pure or mostly pure Python modules where practical. They must not depend on Streamlit or Gemini.

## Suggested modules
- `app/main.py`: FastAPI application and router registration
- `app/api/`: route handlers
- `app/schemas/`: Pydantic input/output models
- `app/models/`: SQLAlchemy models
- `app/db/`: engine, session, base and migrations configuration
- `app/repositories/`: persistence queries
- `app/services/workouts.py`: workout use cases
- `app/analytics/`: workload, estimated strength, trend and flag calculations
- `app/evidence/`: evidence payload builder and validation
- `app/llm/gemini.py`: Gemini adapter with timeout/error handling
- `ui/`: Streamlit pages and API client
- `tests/`: unit, integration, and API tests

Adapt paths to the actual repository rather than forcing a rewrite.

## Data model baseline
- User: only if authentication/multi-user support is in scope; do not add insecure placeholder auth.
- WorkoutSession: id, user_id if applicable, performed_at, notes (optional), created_at.
- Exercise: id, name, normalized_name or stable key, equipment/movement metadata if needed.
- WorkoutSet: id, session_id, exercise_id, set_index, reps, load, optional RPE, optional duration/distance where relevant.
- RecoveryEntry: optional date, sleep duration/quality, soreness, stress, energy, free-text note with strict privacy care.
- InsightRun or InsightRecord: optional persisted evidence/version/status if useful.

Use appropriate foreign keys, indexes, constraints, timestamps, and migration scripts. Units must be explicit and consistent. Decide whether bodyweight is included in load calculations and document that choice.

## API direction
Potential routes:
- `GET /health`
- `GET/POST /workouts`
- `GET /exercises`
- `GET /analytics/exercises/{exercise_id}`
- `POST /insights/analyze`
- `GET /insights/{insight_id}` if insights are persisted

Use request/response models, pagination where appropriate, validation, and consistent error responses. Do not implement routes that the current milestone does not need.

## Analytics contract
- Workload volume for a set can be computed as `load × reps`; aggregate only comparable units and explain exclusions.
- Epley estimated 1RM may be computed as `load × (1 + reps / 30)` within a documented rep range. It is an estimate, not a measured max.
- Plateau and anomaly rules must be explicit, configurable, and tested. Require enough history before flagging.
- A volume spike threshold such as >30% versus the mean of the previous four eligible weeks is a heuristic, not a universal truth.
- A z-score rule such as `abs(z) >= 2` should require sufficient valid historical observations and handle zero variance.
- Do not compare unlike exercises, units, equipment contexts, or rep ranges without clearly stating the limitation.

## Evidence payload
Provide structured, validated facts such as:
- insight type and rule version
- exercise and date/window
- observed value and baseline value
- absolute and percentage difference when defined
- sample count and excluded/missing data
- threshold/rule that triggered the flag
- supporting observations and caveats

Gemini must receive this payload, not raw database access. Validate its response and never let it change computed metrics or flags.


## Current implementation snapshot (2026-10-29)
- `app/models/entities.py` contains users, exercises, workout sessions, sets, recovery logs, and persisted insights.
- `app/security.py` uses Argon2 password hashes and expiring HS256 JWT bearer tokens.
- `app/api/routes/` exposes auth, exercise, workout, recovery, analytics, and insight routes.
- `app/analytics/` includes volume/estimated-1RM calculations plus volume-spike, plateau, and population-z-score rules.
- `app/evidence.py` constructs a Pydantic-validated evidence payload.
- `app/llm/gemini.py` is optional and only receives the minimized evidence object.
- `alembic/versions/0001_initial_schema.py` defines the initial persistence schema.
- Streamlit is currently a single multi-tab page, not a multi-page application.

## Important current behavior
- Workout set loads are stored in kilograms. Bodyweight and assisted sets are explicit and excluded from external-load volume.
- Exercise records are either system-owned (`owner_id` is null, `is_system=true`) or owned by one user.
- Custom exercise access and all workout/recovery/insight queries are scoped to the authenticated user.
- Volume analysis uses the latest five weeks with eligible logged sets; absent weeks are omitted rather than treated as zero.
- The `insights/analyze` route currently persists volume-spike or insufficient-data findings; plateau and anomaly rules are not yet wired to persistence.
