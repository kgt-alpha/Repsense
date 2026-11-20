from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Exercise, User, WorkoutSession, WorkoutSet
from app.schemas import WorkoutCreate, WorkoutRead
from app.security import get_current_user

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _owned_workout_query(user_id: int, workout_id: int):
    return (
        select(WorkoutSession)
        .where(WorkoutSession.id == workout_id, WorkoutSession.user_id == user_id)
        .options(selectinload(WorkoutSession.sets))
    )


@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(
    payload: WorkoutCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise_ids = {item.exercise_id for item in payload.sets}
    allowed = set(
        db.scalars(
            select(Exercise.id).where(
                Exercise.id.in_(exercise_ids),
                (Exercise.is_system.is_(True)) | (Exercise.owner_id == user.id),
            )
        ).all()
    )
    if allowed != exercise_ids:
        raise HTTPException(status_code=422, detail="One or more exercises are unavailable")
    workout = WorkoutSession(user_id=user.id, performed_at=payload.performed_at, notes=payload.notes)
    for item in payload.sets:
        workout.sets.append(
            WorkoutSet(
                exercise_id=item.exercise_id,
                set_number=item.set_number,
                weight_kg=item.weight,
                reps=item.reps,
                is_bodyweight=item.is_bodyweight,
                is_assisted=item.is_assisted,
                rpe=item.rpe,
                notes=item.notes,
            )
        )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return db.scalar(_owned_workout_query(user.id, workout.id))


@router.get("", response_model=list[WorkoutRead])
def list_workouts(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    query = select(WorkoutSession).where(WorkoutSession.user_id == user.id)
    if start_date:
        query = query.where(WorkoutSession.performed_at >= start_date)
    if end_date:
        query = query.where(WorkoutSession.performed_at <= end_date)
    query = query.options(selectinload(WorkoutSession.sets)).order_by(
        WorkoutSession.performed_at.desc(), WorkoutSession.id.desc()
    ).limit(limit).offset(offset)
    return list(db.scalars(query).all())


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(
    workout_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = db.scalar(_owned_workout_query(user.id, workout_id))
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = db.scalar(select(WorkoutSession).where(
        WorkoutSession.id == workout_id, WorkoutSession.user_id == user.id
    ))
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
    return None
