from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.volume import LoadedSet, epley_estimated_1rm, set_volume
from app.database import get_db
from app.models import Exercise, User, WorkoutSession, WorkoutSet
from app.schemas import ExerciseProgressRead, ProgressPoint
from app.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/exercises/{exercise_id}", response_model=ExerciseProgressRead)
def exercise_progress(
    exercise_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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

    points = []
    total_volume = 0.0
    for workout, item in rows:
        loaded = LoadedSet(
            weight_kg=item.weight_kg,
            reps=item.reps,
            is_bodyweight=item.is_bodyweight,
            is_assisted=item.is_assisted,
        )
        volume = set_volume(loaded) if not (item.is_bodyweight or item.is_assisted) else None
        if volume is not None:
            total_volume += volume
        estimated = None
        if not item.is_bodyweight and not item.is_assisted and item.weight_kg is not None:
            estimated = epley_estimated_1rm(item.weight_kg, item.reps)
        points.append(ProgressPoint(
            performed_at=workout.performed_at,
            workout_id=workout.id,
            set_id=item.id,
            reps=item.reps,
            weight_kg=item.weight_kg,
            estimated_1rm_kg=estimated,
            set_volume_kg_reps=volume,
        ))
    return ExerciseProgressRead(
        exercise_id=exercise.id,
        exercise_name=exercise.name,
        points=points,
        eligible_loaded_volume_kg_reps=total_volume,
        note="Volume excludes bodyweight and assisted sets. Estimated 1RM is an estimate and is omitted above 10 reps.",
    )


from datetime import date
from dataclasses import asdict
from app.analytics.rules import performance_anomaly, possible_plateau


def _session_performance(rows):
    """Return one comparable performance value per workout, using best eligible e1RM."""
    by_workout = {}
    for workout, item in rows:
        if workout.performed_at > date.today():
            continue
        if item.is_bodyweight or item.is_assisted or item.weight_kg is None:
            continue
        estimate = epley_estimated_1rm(item.weight_kg, item.reps)
        if estimate is None:
            continue
        by_workout.setdefault(workout.id, (workout.performed_at, estimate))
        if estimate > by_workout[workout.id][1]:
            by_workout[workout.id] = (workout.performed_at, estimate)
    return sorted(by_workout.values(), key=lambda item: item[0])


def _load_exercise_rows(exercise_id: int, user: User, db: Session):
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
    return exercise, rows


@router.get("/exercises/{exercise_id}/performance-anomaly")
def exercise_performance_anomaly(
    exercise_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare latest eligible workout performance with six prior workouts."""
    exercise, rows = _load_exercise_rows(exercise_id, user, db)
    sessions = _session_performance(rows)
    if not sessions:
        finding = performance_anomaly(0.0, [])
        dates = []
    else:
        current_date, current_value = sessions[-1]
        prior = sessions[:-1]
        finding = performance_anomaly(current_value, [value for _, value in prior[-6:]])
        dates = [day.isoformat() for day, _ in prior[-6:]] + [current_date.isoformat()]
    payload = asdict(finding)
    payload.update({"exercise_id": exercise.id, "exercise_name": exercise.name,
                    "observation_dates": dates,
                    "note": "Estimated 1RM is a proxy, not a measured maximum. An anomaly does not establish its cause."})
    return payload


@router.get("/exercises/{exercise_id}/plateau")
def exercise_possible_plateau(
    exercise_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check the four latest comparable workouts for a possible performance plateau."""
    exercise, rows = _load_exercise_rows(exercise_id, user, db)
    sessions = _session_performance(rows)
    recent = sessions[-4:]
    finding = possible_plateau([value for _, value in recent])
    payload = asdict(finding)
    payload.update({"exercise_id": exercise.id, "exercise_name": exercise.name,
                    "observation_dates": [day.isoformat() for day, _ in recent],
                    "note": "Heuristic based on estimated 1RM across recent workouts; it is not a diagnosis or proof of stalled adaptation."})
    return payload
