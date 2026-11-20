# Engineering Rules

## Implementation
- Keep API routes thin and place deterministic calculations in independent modules.
- Inspect existing behavior before changing it; prefer focused, backwards-compatible changes.
- Use complete validation, explicit units, and clear error responses.
- Keep missing measurements missing; do not silently convert them to zero.
- Scope every user-owned query to the authenticated user.
- Use Alembic for database schema changes.

## Analytics and explanations
- Backend analytics own metrics, thresholds, and classifications.
- Every insight must retain its evidence, comparison window, sample count, and limitations.
- Gemini is optional and may explain only supplied evidence.
- Never present heuristic findings as diagnoses, causal claims, or prescriptions.

## Testing and delivery
- Test boundaries, invalid inputs, missing history, date handling, ownership, and provider failures.
- Mock external AI calls in automated tests.
- Report only tests actually executed and preserve known limitations in the progress tracker.
- Do not commit changes unless explicitly requested.
