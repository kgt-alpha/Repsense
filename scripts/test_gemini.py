"""Check the Gemini explanation path on its own (no database, no login needed).

Run from the project root, with the venv active:
    python scripts/test_gemini.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from app.config import get_settings  # noqa: E402
from app.llm.gemini import ExplanationRejected, ExplanationUnavailable, explain_evidence  # noqa: E402

settings = get_settings()
print(f"Model: {settings.gemini_model}")
print(f"API key set: {bool(settings.gemini_api_key)}")

evidence = {
    "finding_type": "volume_spike", "metric_name": "weekly_volume",
    "current_value": 660, "baseline_value": 480, "percentage_change": 37.5,
    "threshold": 30, "triggered": True, "sufficient_data": True, "observation_count": 4,
    "prior_weeks_found": 4, "prior_weeks_required": 4,
    "eligible_week_starts": ["2026-10-12", "2026-10-19", "2026-10-26", "2026-11-02", "2026-11-09"],
    "exercise_name": "Incline DB press",
}
try:
    result = explain_evidence(evidence)
    if result is None:
        print("RESULT: skipped (no API key found in .env)")
    else:
        print("RESULT: OK\n", result.model_dump_json(indent=2))
except ExplanationRejected as exc:
    print("RESULT: Gemini answered but validation rejected it ->", exc)
except ExplanationUnavailable as exc:
    print("RESULT: Gemini call FAILED ->", exc, "\n(see the ERROR traceback above for the real cause)")