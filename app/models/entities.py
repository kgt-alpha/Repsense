from datetime import date, datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index
from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    exercises: Mapped[list["Exercise"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    workouts: Mapped[list["WorkoutSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    recovery_logs: Mapped[list["RecoveryLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    insights: Mapped[list["Insight"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (UniqueConstraint("owner_id", "normalized_name", name="uq_exercise_owner_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(120), nullable=False)
    muscle_group: Mapped[str | None] = mapped_column(String(80))
    equipment: Mapped[str | None] = mapped_column(String(80))
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    owner: Mapped[User | None] = relationship(back_populates="exercises")
    sets: Mapped[list["WorkoutSet"]] = relationship(back_populates="exercise")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    __table_args__ = (Index("ix_workouts_user_date", "user_id", "performed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    performed_at: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="workouts")
    sets: Mapped[list["WorkoutSet"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class WorkoutSet(Base):
    __tablename__ = "sets"
    __table_args__ = (
        CheckConstraint("reps > 0", name="ck_sets_reps_positive"),
        CheckConstraint("set_number > 0", name="ck_sets_number_positive"),
        CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="ck_sets_weight_nonnegative"),
        CheckConstraint("rpe IS NULL OR (rpe >= 1 AND rpe <= 10)", name="ck_sets_rpe_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False, index=True)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    is_bodyweight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_assisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rpe: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    session: Mapped[WorkoutSession] = relationship(back_populates="sets")
    exercise: Mapped[Exercise] = relationship(back_populates="sets")


class RecoveryLog(Base):
    __tablename__ = "recovery_logs"
    __table_args__ = (
        CheckConstraint("sleep_hours IS NULL OR (sleep_hours >= 0 AND sleep_hours <= 24)", name="ck_recovery_sleep_range"),
        CheckConstraint("energy_score IS NULL OR (energy_score >= 1 AND energy_score <= 10)", name="ck_recovery_energy_range"),
        CheckConstraint("soreness_score IS NULL OR (soreness_score >= 1 AND soreness_score <= 10)", name="ck_recovery_soreness_range"),
        CheckConstraint("resting_heart_rate IS NULL OR (resting_heart_rate > 0 AND resting_heart_rate < 300)", name="ck_recovery_rhr_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    energy_score: Mapped[int | None] = mapped_column(Integer)
    soreness_score: Mapped[int | None] = mapped_column(Integer)
    resting_heart_rate: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="recovery_logs")


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="calculated", nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_json: Mapped[str | None] = mapped_column(Text)
    analytics_version: Mapped[str] = mapped_column(String(30), default="0.1.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="insights")
