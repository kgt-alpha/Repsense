from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class LoadedSet:
    weight_kg: float | None
    reps: int
    is_bodyweight: bool = False
    is_assisted: bool = False


def set_volume(item: LoadedSet) -> float | None:
    """External-load volume in kg-reps; bodyweight and assisted sets are excluded."""
    if item.is_bodyweight or item.is_assisted:
        return None
    if item.weight_kg is None or item.weight_kg <= 0 or item.reps <= 0:
        raise ValueError("externally loaded sets require positive weight and reps")
    return item.weight_kg * item.reps


def total_volume(sets: Iterable[LoadedSet]) -> float:
    return sum(value for item in sets if (value := set_volume(item)) is not None)


def epley_estimated_1rm(weight_kg: float, reps: int, *, max_reps: int = 10) -> float | None:
    """Return Epley estimated 1RM for 1..max_reps; this is not a measured max."""
    if weight_kg <= 0 or reps <= 0:
        raise ValueError("weight and reps must be positive")
    if reps > max_reps:
        return None
    return weight_kg * (1 + reps / 30)
