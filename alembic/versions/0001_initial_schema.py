"""Initial RepSense persistence schema.

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("normalized_name", sa.String(length=120), nullable=False),
        sa.Column("muscle_group", sa.String(length=80)),
        sa.Column("equipment", sa.String(length=80)),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("owner_id", "normalized_name", name="uq_exercise_owner_name"),
    )
    op.create_index("ix_exercises_owner_id", "exercises", ["owner_id"])

    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("performed_at", sa.Date(), nullable=False),
        sa.Column("notes", sa.String(length=1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workouts_user_date", "workout_sessions", ["user_id", "performed_at"])

    op.create_table(
        "sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workout_session_id", sa.Integer(), sa.ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_id", sa.Integer(), sa.ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float()),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("is_bodyweight", sa.Boolean(), nullable=False),
        sa.Column("is_assisted", sa.Boolean(), nullable=False),
        sa.Column("rpe", sa.Float()),
        sa.Column("notes", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("reps > 0", name="ck_sets_reps_positive"),
        sa.CheckConstraint("set_number > 0", name="ck_sets_number_positive"),
        sa.CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="ck_sets_weight_nonnegative"),
        sa.CheckConstraint("rpe IS NULL OR (rpe >= 1 AND rpe <= 10)", name="ck_sets_rpe_range"),
    )
    op.create_index("ix_sets_workout_session_id", "sets", ["workout_session_id"])
    op.create_index("ix_sets_exercise_id", "sets", ["exercise_id"])

    op.create_table(
        "recovery_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.Date(), nullable=False),
        sa.Column("sleep_hours", sa.Float()),
        sa.Column("energy_score", sa.Integer()),
        sa.Column("soreness_score", sa.Integer()),
        sa.Column("resting_heart_rate", sa.Integer()),
        sa.Column("notes", sa.String(length=1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("sleep_hours IS NULL OR (sleep_hours >= 0 AND sleep_hours <= 24)", name="ck_recovery_sleep_range"),
        sa.CheckConstraint("energy_score IS NULL OR (energy_score >= 1 AND energy_score <= 10)", name="ck_recovery_energy_range"),
        sa.CheckConstraint("soreness_score IS NULL OR (soreness_score >= 1 AND soreness_score <= 10)", name="ck_recovery_soreness_range"),
        sa.CheckConstraint("resting_heart_rate IS NULL OR (resting_heart_rate > 0 AND resting_heart_rate < 300)", name="ck_recovery_rhr_range"),
    )
    op.create_index("ix_recovery_logs_user_id", "recovery_logs", ["user_id"])
    op.create_index("ix_recovery_logs_recorded_at", "recovery_logs", ["recorded_at"])

    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("insight_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("evidence_json", sa.Text(), nullable=False),
        sa.Column("explanation_json", sa.Text()),
        sa.Column("analytics_version", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_insights_user_id", "insights", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_insights_user_id", table_name="insights")
    op.drop_table("insights")
    op.drop_index("ix_recovery_logs_recorded_at", table_name="recovery_logs")
    op.drop_index("ix_recovery_logs_user_id", table_name="recovery_logs")
    op.drop_table("recovery_logs")
    op.drop_index("ix_sets_exercise_id", table_name="sets")
    op.drop_index("ix_sets_workout_session_id", table_name="sets")
    op.drop_table("sets")
    op.drop_index("ix_workouts_user_date", table_name="workout_sessions")
    op.drop_table("workout_sessions")
    op.drop_index("ix_exercises_owner_id", table_name="exercises")
    op.drop_table("exercises")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
