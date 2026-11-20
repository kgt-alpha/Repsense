import pytest

from app.llm.gemini import ExplanationUnavailable, _validate_numeric_claims
from app.schemas import InsightExplanation


@pytest.fixture
def evidence():
    return {
        "finding_type": "volume_spike",
        "triggered": True,
        "sufficient_data": True,
        "current_value": 1500.0,
        "baseline_value": 1000.0,
        "percentage_change": 50.0,
        "threshold": 30.0,
        "observation_count": 4,
    }


def test_explanation_accepts_only_numbers_supported_by_metric_evidence(evidence):
    explanation = InsightExplanation(
        title="Weekly volume increased",
        summary="The current value is 1500 kg-reps, compared with 1000 kg-reps; change is 50%.",
        evidence_points=["The 50% change exceeds the 30% threshold."],
        uncertainty="This does not predict injury.",
        next_checks=["Review the logged sessions."],
    )
    _validate_numeric_claims(explanation, evidence)


def test_explanation_rejects_unsupported_numeric_claim(evidence):
    explanation = InsightExplanation(
        title="Weekly volume increased",
        summary="You should reduce training by 20%.",
        evidence_points=[],
        uncertainty="This is not a diagnosis.",
        next_checks=[],
    )
    with pytest.raises(ExplanationUnavailable):
        _validate_numeric_claims(explanation, evidence)
