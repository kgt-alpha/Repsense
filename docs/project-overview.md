# Project Overview

## Purpose
RepSense turns logged gym sessions into understandable personal strength-performance insights. It highlights trends, possible plateaus, unusual workload changes, and performance dips relative to a user's own baseline.

## Target user
A gym-goer who logs exercises, sets, reps, load, and dates and wants to understand whether performance is improving, stable, or changing.

## MVP outcomes
- Record and browse workout sessions and sets.
- Track exercise-level performance over time.
- Compute transparent workload and estimated-strength metrics.
- Flag possible plateaus, volume spikes, and unusual performance dips using explicit rules.
- Show the evidence behind each insight.
- Optionally add user-entered recovery context, clearly labeled as context rather than proof of cause.
- Generate a concise Gemini explanation grounded only in the evidence payload.

## Out of scope
- Medical diagnosis or treatment advice.
- Claims that a recovery factor caused a performance change.
- Automatic workout plans or prescriptions.
- A custom machine-learning model.
- Social feeds, leaderboards, or complex wearable integrations in the MVP.

## Product principles
1. Personal baseline beats unsupported universal comparisons.
2. Explain every insight with dates, metrics, comparison windows, and limitations.
3. Missing data is not zero.
4. Avoid false precision and overstated certainty.
5. Users should still get useful deterministic results when Gemini is unavailable.

## MVP success
A user can enter or load sample workouts, inspect a metric trend, see why a flag was raised, and receive a cautious explanation that cites only backend evidence.
