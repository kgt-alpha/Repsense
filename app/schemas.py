from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    muscle_group: str | None = Field(default=None, max_length=80)
    equipment: str | None = Field(default=None, max_length=80)


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    muscle_group: str | None
    equipment: str | None
    is_system: bool


class SetCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    set_number: int = Field(gt=0, le=100)
    weight: float | None = Field(default=None, ge=0, le=1000, description="Weight in kilograms; null for bodyweight sets")
    reps: int = Field(gt=0, le=1000)
    is_bodyweight: bool = False
    is_assisted: bool = False
    rpe: float | None = Field(default=None, ge=1, le=10)
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_weight_representation(self):
        if self.is_bodyweight and self.weight is not None:
            raise ValueError("bodyweight sets must omit external weight")
        if not self.is_bodyweight and not self.is_assisted and self.weight is None:
            raise ValueError("weight is required for externally loaded sets")
        return self


class WorkoutCreate(BaseModel):
    performed_at: date
    notes: str | None = Field(default=None, max_length=1000)
    sets: list[SetCreate] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def validate_workout_date_and_set_numbers(self):
        if self.performed_at > date.today():
            raise ValueError("performed_at cannot be in the future")
        numbers = [item.set_number for item in self.sets]
        if len(numbers) != len(set(numbers)):
            raise ValueError("set_number values must be unique within a workout")
        return self


class SetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    exercise_id: int
    set_number: int
    weight_kg: float | None
    reps: int
    is_bodyweight: bool
    is_assisted: bool
    rpe: float | None
    notes: str | None


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    performed_at: date
    notes: str | None
    created_at: datetime
    sets: list[SetRead]


class RecoveryCreate(BaseModel):
    recorded_at: date
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    energy_score: int | None = Field(default=None, ge=1, le=10)
    soreness_score: int | None = Field(default=None, ge=1, le=10)
    resting_heart_rate: int | None = Field(default=None, gt=0, lt=300)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_recorded_date(self):
        if self.recorded_at > date.today():
            raise ValueError("recorded_at cannot be in the future")
        return self


class RecoveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recorded_at: date
    sleep_hours: float | None
    energy_score: int | None
    soreness_score: int | None
    resting_heart_rate: int | None
    notes: str | None
    created_at: datetime


from typing import Literal


class ProgressPoint(BaseModel):
    performed_at: date
    workout_id: int
    set_id: int
    reps: int
    weight_kg: float | None
    estimated_1rm_kg: float | None
    set_volume_kg_reps: float | None


class ExerciseProgressRead(BaseModel):
    exercise_id: int
    exercise_name: str
    points: list[ProgressPoint]
    eligible_loaded_volume_kg_reps: float
    note: str


class InsightExplanation(BaseModel):
    title: str = Field(max_length=120)
    summary: str = Field(max_length=1000)
    evidence_points: list[str] = Field(max_length=8)
    uncertainty: str = Field(max_length=500)
    next_checks: list[str] = Field(max_length=5)


class InsightRead(BaseModel):
    id: int
    insight_type: str
    status: str
    evidence: dict
    explanation: InsightExplanation | None = None
    confidence: Literal["low", "medium", "high"]
    created_at: datetime
