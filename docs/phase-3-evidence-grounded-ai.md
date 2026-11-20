# Phase 3 — Evidence-grounded AI

## Scope

Gemini is an optional explanation layer. Backend analytics remain the source of truth for metrics and findings. The explanation function:

- skips untriggered or insufficient-data findings;
- passes a bounded, serialized evidence payload to the provider;
- explicitly treats evidence as data rather than instructions;
- requests structured output using `InsightExplanation`;
- rejects numeric claims that are not present in the finding's metric fields;
- returns a generic unavailable error without exposing prompts, evidence, or credentials.

If the Gemini key is absent or the provider returns invalid output, the API retains deterministic evidence and marks the explanation unavailable.

## Files changed in this phase

- `app/llm/gemini.py`
- `tests/test_llm_grounding.py`
- `docs/phase-3-evidence-grounded-ai.md`

The phase package is a full project snapshot based on Phase 2. Run the complete suite and verify a real Gemini request during the final integration phase.
