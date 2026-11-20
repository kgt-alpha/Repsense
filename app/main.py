from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import analytics, auth, exercises, insights, recovery, workouts
from app.config import get_settings
from app.database import database_is_ready

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description=(
        "Workout performance and recovery insights grounded in deterministic analytics. "
        "Not a medical diagnosis system."
    ),
    version="0.2.0",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(exercises.router, prefix=settings.api_v1_prefix)
app.include_router(workouts.router, prefix=settings.api_v1_prefix)
app.include_router(recovery.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(insights.router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Process-level health check; does not require the database."""
    return {"status": "ok", "service": "repsense-api"}


@app.get("/ready", tags=["system"])
def readiness():
    """Dependency readiness is reported separately from process health."""
    if not database_is_ready():
        return JSONResponse(status_code=503, content={"status": "not_ready", "dependency": "database"})
    return {"status": "ready", "dependency": "database"}


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "RepSense API is running", "docs": "/docs"}
