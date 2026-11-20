from dataclasses import dataclass
from statistics import mean, pstdev


@dataclass(frozen=True)
class Finding:
    finding_type: str
    metric_name: str
    current_value: float | None
    baseline_value: float | None
    percentage_change: float | None
    threshold: float | None
    triggered: bool
    sufficient_data: bool
    observation_count: int
    rule: str
    limitations: tuple[str, ...] = ()


def volume_spike(
    current_week_volume: float | None,
    previous_eligible_week_volumes: list[float],
    threshold_percent: float = 30.0,
) -> Finding:
    """Compare the current week with the mean of the four preceding eligible weeks."""
    history = previous_eligible_week_volumes[-4:]
    if current_week_volume is None or len(history) < 4:
        return Finding("insufficient_data", "weekly_volume", current_week_volume, None, None,
                       threshold_percent, False, False, len(history),
                       "Requires current week and four prior eligible weeks.",
                       ("Missing weeks are not treated as zero-volume weeks.",))
    baseline = mean(history)
    if baseline <= 0:
        return Finding("insufficient_data", "weekly_volume", current_week_volume, baseline, None,
                       threshold_percent, False, False, 4, "Positive baseline required.",
                       ("Percentage change is undefined for a zero baseline.",))
    change = (current_week_volume - baseline) / baseline * 100
    triggered = change > threshold_percent
    return Finding("volume_spike" if triggered else "no_volume_spike", "weekly_volume",
                   current_week_volume, baseline, change, threshold_percent, triggered, True, 4,
                   f"Trigger only when percentage change is strictly greater than {threshold_percent}%.",
                   ("Training-load observation only; not an injury-risk prediction.",))


def performance_anomaly(
    current_value: float,
    prior_values: list[float],
    min_observations: int = 6,
    z_threshold: float = 2.0,
) -> Finding:
    """Population-z-score against prior values only; negative z suggests a performance dip."""
    if len(prior_values) < min_observations:
        return Finding("insufficient_data", "performance_metric", current_value, None, None,
                       z_threshold, False, False, len(prior_values),
                       f"Requires at least {min_observations} prior eligible observations.")
    baseline = mean(prior_values)
    deviation = pstdev(prior_values)
    if deviation == 0:
        return Finding("insufficient_data", "performance_metric", current_value, baseline, None,
                       z_threshold, False, False, len(prior_values),
                       "Zero population standard deviation; z-score is undefined.")
    z_score = (current_value - baseline) / deviation
    triggered = abs(z_score) >= z_threshold
    return Finding("performance_dip" if triggered and z_score < 0 else
                   "performance_anomaly" if triggered else "no_anomaly",
                   "performance_metric_z_score", z_score, 0.0, None, z_threshold, triggered,
                   True, len(prior_values),
                   f"Trigger when absolute population z-score is at least {z_threshold}.",
                   ("An anomaly is a deviation, not proof of fatigue, injury, or cause.",))


def possible_plateau(values: list[float], min_sessions: int = 4, meaningful_change_percent: float = 2.0) -> Finding:
    """Flag only if latest eligible values show no >= threshold improvement from first."""
    if len(values) < min_sessions:
        return Finding("insufficient_data", "performance_metric", values[-1] if values else None,
                       values[0] if values else None, None, meaningful_change_percent, False, False,
                       len(values), f"Requires at least {min_sessions} comparable sessions.")
    baseline, current = values[0], values[-1]
    if baseline <= 0:
        return Finding("insufficient_data", "performance_metric", current, baseline, None,
                       meaningful_change_percent, False, False, len(values), "Positive baseline required.")
    change = (current - baseline) / baseline * 100
    triggered = change < meaningful_change_percent
    return Finding("plateau" if triggered else "progression", "performance_metric", current, baseline,
                   change, meaningful_change_percent, triggered, True, len(values),
                   f"Possible plateau if change over {len(values)} comparable sessions is below {meaningful_change_percent}%.",
                   ("Heuristic only; comparable sessions and metric selection matter.",))
