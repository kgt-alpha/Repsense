from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exercise, User
from app.schemas import ExerciseCreate, ExerciseRead
from app.security import get_current_user

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    search: str | None = Query(default=None, max_length=120),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Exercise).where(or_(Exercise.is_system.is_(True), Exercise.owner_id == user.id))
    if search:
        query = query.where(Exercise.name.ilike(f"%{search.strip()}%"))
    return list(db.scalars(query.order_by(Exercise.name).limit(100)).all())


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(
    payload: ExerciseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    normalized = " ".join(payload.name.split()).casefold()
    existing = db.scalar(
        select(Exercise).where(Exercise.owner_id == user.id, Exercise.normalized_name == normalized)
    )
    if existing:
        raise HTTPException(status_code=409, detail="You already have an exercise with this name")
    exercise = Exercise(
        name=" ".join(payload.name.split()),
        normalized_name=normalized,
        muscle_group=payload.muscle_group,
        equipment=payload.equipment,
        owner_id=user.id,
        is_system=False,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise
