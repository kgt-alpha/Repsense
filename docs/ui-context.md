# UI Context

## Streamlit direction
The UI should feel calm, clear, and data-led. Favor a simple dashboard over a dense analytics console.

## Main screens
1. **Overview** — recent sessions, a small number of meaningful trends, and current insight flags.
2. **Log workout** — session date, exercise, sets, reps, load and optional RPE; make units explicit.
3. **Exercise detail** — history chart, recent sessions, estimated-strength trend, and comparable baseline.
4. **Insight detail** — what was observed, what it was compared with, the rule that fired, evidence, uncertainty, and optional AI explanation.
5. **Recovery context** — optional user-entered context, clearly separated from measured workout facts.

## UX rules
- Show units and date ranges on every chart.
- Make it possible to inspect the raw values behind a chart or insight.
- Label estimated 1RM as an estimate.
- Explain why an insight was raised and when there is insufficient history.
- Use empty states with a clear next action.
- Provide understandable loading, API-error, and Gemini-unavailable states.
- Never present a heuristic flag as a diagnosis or certainty.
- Avoid clutter, unnecessary animation, and alarmist colors/copy.
- Preserve user input on recoverable errors where possible.
- Ensure controls have labels and useful validation messages.

## Chart guidance
Use consistent scales and labels. Do not draw a trend line through missing data as if it were measured. Avoid comparing incomparable units. If data points are too sparse, show the points and state that there is not enough history for a reliable trend.
