import pytest
from app.analytics.volume import LoadedSet, set_volume, total_volume, epley_estimated_1rm
from app.analytics.rules import volume_spike, performance_anomaly, possible_plateau
from app.evidence import build_evidence


def test_loaded_volume_excludes_bodyweight_and_assisted_sets():
    sets = [LoadedSet(50, 8), LoadedSet(40, 10), LoadedSet(None, 10, is_bodyweight=True),
            LoadedSet(None, 8, is_assisted=True)]
    assert set_volume(sets[0]) == 400
    assert total_volume(sets) == 800


def test_invalid_volume_and_estimated_1rm():
    with pytest.raises(ValueError):
        set_volume(LoadedSet(0, 8))
    assert epley_estimated_1rm(60, 5) == pytest.approx(70)
    assert epley_estimated_1rm(60, 12) is None
    with pytest.raises(ValueError):
        epley_estimated_1rm(60, 0)


def test_volume_spike_threshold_and_sparse_data():
    assert volume_spike(131, [100, 100, 100, 100]).triggered
    assert not volume_spike(130, [100, 100, 100, 100]).triggered
    assert not volume_spike(200, [100, 100, 100]).sufficient_data
    assert not volume_spike(100, [0, 0, 0, 0]).sufficient_data


def test_performance_anomaly_uses_prior_values_and_handles_zero_variance():
    assert not performance_anomaly(10, [10, 10, 10, 10, 10]).sufficient_data
    assert not performance_anomaly(9, [10] * 6).sufficient_data
    result = performance_anomaly(5, [10, 11, 9, 10, 12, 8])
    assert result.triggered
    assert result.finding_type == "performance_dip"


def test_plateau_and_evidence_payload_are_traceable():
    finding = possible_plateau([100, 100, 101, 100])
    assert finding.triggered
    evidence = build_evidence(finding)
    assert evidence.finding_type == "plateau"
    assert evidence.current_value == 100
    assert evidence.observation_count == 4
