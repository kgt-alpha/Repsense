import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.rules import volume_spike
from app.analytics.volume import LoadedSet, set_volume
from app.database import get_db
from app.llm.gemini import ExplanationRejected, ExplanationUnavailable, explain_evidence
from app.models import Exercise, Insight, User, WorkoutSession, WorkoutSet
from app.schemas import InsightExplanation, InsightRead
from app.security import get_current_user
from app.evidence import build_evidence

router = APIRouter(prefix="/insights", tags=["insights"])


def _confidence(evidence: dict) -> str:
    if not evidence.get("sufficient_data"):
        return "low"
    if evidence.get("observation_count", 0) >= 8:
        return "high"
    return "medium"


def _read_record(record: Insight) -> InsightRead:
    evidence = json.loads(record.evidence_json)
    explanation = InsightExplanation.model_validate_json(record.explanation_json) if record.explanation_json else None
    return InsightRead(
        id=record.id,
        insight_type=record.insight_type,
        status=record.status,
        evidence=evidence,
        explanation=explanation,
        confidence=_confidence(evidence),
        created_at=record.created_at,
    )


@router.post("/analyze", response_model=InsightRead, status_code=status.HTTP_201_CREATED)
def analyze_volume(
    exercise_id: int = Query(gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze volume for an exercise using the latest five eligible workout weeks."""
    exercise = db.scalar(select(Exercise).where(
        Exercise.id == exercise_id,
        (Exercise.is_system.is_(True)) | (Exercise.owner_id == user.id),
    ))
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    rows = db.execute(
        select(WorkoutSession, WorkoutSet)
        .join(WorkoutSet, WorkoutSet.workout_session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user.id, WorkoutSet.exercise_id == exercise_id)
        .order_by(WorkoutSession.performed_at, WorkoutSet.set_number)
    ).all()

    # Only completed/current calendar weeks are eligible. Future-dated sessions
    # must never become the "current" observation or baseline evidence.
    current_monday = date.today() - timedelta(days=date.today().weekday())
    weekly: dict[date, float] = {}
    for workout, item in rows:
        if workout.performed_at > date.today():
            continue
        if item.is_bodyweight or item.is_assisted or item.weight_kg is None:
            continue
        volume = set_volume(LoadedSet(item.weight_kg, item.reps))
        monday = workout.performed_at - timedelta(days=workout.performed_at.weekday())
        weekly[monday] = weekly.get(monday, 0.0) + (volume or 0.0)

    # The current week is a calendar week, not the most recent week with data.
    # Baseline weeks are the four most recent eligible weeks strictly before it;
    # missing weeks are omitted rather than silently treated as zero.
    current = weekly.get(current_monday)
    prior_week_starts = sorted(
        (week_start for week_start in weekly if week_start < current_monday),
        reverse=True,
    )[:4]
    history = [weekly[week_start] for week_start in reversed(prior_week_starts)]
    finding = volume_spike(current, history)
    eligible_week_starts = [week_start.isoformat() for week_start in prior_week_starts[::-1]]
    if current is not None:
        eligible_week_starts.append(current_monday.isoformat())
    evidence_model = build_evidence(finding)
    evidence = evidence_model.model_dump(mode="json")
    evidence["exercise_id"] = exercise.id
    evidence["exercise_name"] = exercise.name
    evidence["eligible_week_starts"] = eligible_week_starts
    evidence["observation_dates"] = eligible_week_starts
    evidence["current_week_start"] = current_monday.isoformat()
    evidence["has_current_week_data"] = current is not None
    evidence["prior_weeks_found"] = len(prior_week_starts)
    evidence["prior_weeks_required"] = 4

    explanation = None
    status_value = "calculated"
    if finding.triggered:
        try:
            explanation_obj = explain_evidence(evidence)
            if explanation_obj is not None:
                explanation = explanation_obj.model_dump(mode="json")
                status_value = "explained"
            else:
                status_value = "ai_not_configured"
        except ExplanationRejected:
            status_value = "ai_rejected"
        except ExplanationUnavailable:
            status_value = "ai_error"

    record = Insight(
        user_id=user.id,
        insight_type=finding.finding_type,
        status=status_value,
        evidence_json=json.dumps(evidence),
        explanation_json=json.dumps(explanation) if explanation else None,
        analytics_version="0.1.0",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _read_record(record)


@router.get("", response_model=list[InsightRead])
def list_insights(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(Insight).where(Insight.user_id == user.id)
        .order_by(Insight.created_at.desc(), Insight.id.desc())
        .limit(limit).offset(offset)
    ).all()
    return [_read_record(record) for record in records]