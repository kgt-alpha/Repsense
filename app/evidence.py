from datetime import date
from pydantic import BaseModel, ConfigDict, Field

from app.analytics.rules import Finding


class EvidencePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    finding_type: str
    metric_name: str
    current_value: float | None
    baseline_value: float | None
    percentage_change: float | None
    threshold: float | None
    triggered: bool
    sufficient_data: bool
    observation_count: int = Field(ge=0)
    rule: str
    observation_dates: list[date] = Field(default_factory=list)
    analytics_version: str = "0.1.0"
    limitations: list[str] = Field(default_factory=list)


def build_evidence(finding: Finding, observation_dates: list[date] | None = None) -> EvidencePayload:
    """Serialize only backend-calculated values; this function performs no analysis."""
    return EvidencePayload(
        finding_type=finding.finding_type,
        metric_name=finding.metric_name,
        current_value=finding.current_value,
        baseline_value=finding.baseline_value,
        percentage_change=finding.percentage_change,
        threshold=finding.threshold,
        triggered=finding.triggered,
        sufficient_data=finding.sufficient_data,
        observation_count=finding.observation_count,
        rule=finding.rule,
        observation_dates=observation_dates or [],
        limitations=list(finding.limitations),
    )
