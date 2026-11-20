"""Add clearly labelled, repeat-safe demo history for one RepSense user.

Run from the RepSense project root inside the API container:
    python -m app.scripts.seed_demo_data
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.database import get_engine
from app.models import Exercise, RecoveryLog, User, WorkoutSession, WorkoutSet

TARGET_EMAIL = "testuser@example.com"
EXERCISE_NAME = "Incline DB press"
MARKER = "[REPSENSE_DEMO_SEED_V1]"


def main() -> None:
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())

    with get_engine().begin() as connection:
        # Use the ORM session bound to the configured application database.
        from sqlalchemy.orm import Session
        db = Session(bind=connection, autoflush=False, expire_on_commit=False)
        try:
            user = db.scalar(select(User).where(User.email == TARGET_EMAIL))
            if user is None:
                raise SystemExit(
                    f"User {TARGET_EMAIL!r} was not found. Register/log in with this account first."
                )

            exercise = db.scalar(
                select(Exercise).where(
                    Exercise.owner_id == user.id,
                    Exercise.name.ilike(EXERCISE_NAME),
                )
            )
            if exercise is None:
                exercise = db.scalar(
                    select(Exercise).where(
                        Exercise.is_system.is_(True),
                        Exercise.name.ilike(EXERCISE_NAME),
                    )
                )
            if exercise is None:
                exercise = Exercise(
                    name=EXERCISE_NAME,
                    normalized_name=EXERCISE_NAME.casefold(),
                    muscle_group="Chest",
                    equipment="Dumbbell",
                    is_system=False,
                    owner_id=user.id,
                )
                db.add(exercise)
                db.flush()

            # Four completed baseline weeks plus the current calendar week.
            # Current volume is intentionally >30% above the prior-four-week mean
            # so the existing volume-spike rule can produce a demo finding.
            weekly_weights = [15.0, 16.0, 16.0, 17.0, 22.0]
            added_workouts = 0
            for weeks_ago, weight in zip((4, 3, 2, 1, 0), weekly_weights):
                performed = current_monday - timedelta(days=7 * weeks_ago)
                note = f"{MARKER} weekly volume demonstration"
                existing = db.scalar(
                    select(WorkoutSession).where(
                        WorkoutSession.user_id == user.id,
                        WorkoutSession.performed_at == performed,
                        WorkoutSession.notes == note,
                    )
                )
                if existing is not None:
                    continue
                session = WorkoutSession(
                    user_id=user.id,
                    performed_at=performed,
                    notes=note,
                )
                db.add(session)
                db.flush()
                for set_number in range(1, 4):
                    db.add(
                        WorkoutSet(
                            workout_session_id=session.id,
                            exercise_id=exercise.id,
                            set_number=set_number,
                            weight_kg=weight,
                            reps=10,
                            is_bodyweight=False,
                            is_assisted=False,
                            rpe=7.0 if weeks_ago else 8.0,
                            notes=f"{MARKER} synthetic demo set",
                        )
                    )
                added_workouts += 1

            # Add a month of clearly labelled recovery history, without duplicating
            # an existing demo row for the same date.
            added_recovery = 0
            for days_ago in range(34, -1, -1):
                recorded = today - timedelta(days=days_ago)
                note = f"{MARKER} synthetic recovery demo"
                exists = db.scalar(
                    select(RecoveryLog.id).where(
                        RecoveryLog.user_id == user.id,
                        RecoveryLog.recorded_at == recorded,
                        RecoveryLog.notes == note,
                    )
                )
                if exists is not None:
                    continue
                # Stable, plausible variation; these are demonstration values only.
                db.add(
                    RecoveryLog(
                        user_id=user.id,
                        recorded_at=recorded,
                        sleep_hours=7.0 + ((days_ago % 5) * 0.25),
                        energy_score=6 + (days_ago % 4),
                        soreness_score=3 + (days_ago % 3),
                        resting_heart_rate=60 + (days_ago % 7),
                        notes=note,
                    )
                )
                added_recovery += 1

            db.commit()
            print("RepSense demo seed completed.")
            print(f"Account: {user.email} (user_id={user.id})")
            print(f"Exercise: {exercise.name} (exercise_id={exercise.id})")
            print(f"Added workout sessions: {added_workouts}")
            print(f"Added recovery logs: {added_recovery}")
            print(f"Current week starts: {current_monday.isoformat()}")
            print("All inserted rows are labelled with [REPSENSE_DEMO_SEED_V1].")
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


if __name__ == "__main__":
    main()
