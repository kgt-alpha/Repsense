from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecoveryLog, User
from app.schemas import RecoveryCreate, RecoveryRead
from app.security import get_current_user

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.post("", response_model=RecoveryRead, status_code=status.HTTP_201_CREATED)
def create_recovery_log(
    payload: RecoveryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = RecoveryLog(user_id=user.id, **payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[RecoveryRead])
def list_recovery_logs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(RecoveryLog)
        .where(RecoveryLog.user_id == user.id)
        .order_by(RecoveryLog.recorded_at.desc(), RecoveryLog.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(query).all())
