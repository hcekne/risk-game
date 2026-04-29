# Strategic Rubric Calibration Notes

## Initial Calibration Pass
Date: `2026-04-23`

This was the first manual calibration pass for the observable-strategy rubric.

## Sample Reviewed
Reviewed saved game:

- [game__2026-04-23_21-54-55](../game_results/rubric_calibration/game__2026-04-23_21-54-55)

Analyzer outputs:

- [strategic_analysis.md](../game_results/rubric_calibration/game__2026-04-23_21-54-55/analysis/strategic_analysis.md)
- [strategic_metrics.json](../game_results/rubric_calibration/game__2026-04-23_21-54-55/analysis/strategic_metrics.json)
- [strategic_turn_scores.json](../game_results/rubric_calibration/game__2026-04-23_21-54-55/analysis/strategic_turn_scores.json)

The calibration sample used deterministic scripted agents because they are cheap, reproducible, and make it easy to verify whether the rubric is rewarding clearly strategic play.

## Reviewed Turns
The following turns were reviewed manually against the rubric output:

1. `Round 1, Turn 1, Charlie`
- Manual judgment: `strong`
- Why: valid plan, two successful attacks, fortify matched plan, positive board gain
- Rubric result: `4.60 / 5`, `strong`
- Verdict: acceptable

2. `Round 1, Turn 2, Alpha`
- Manual judgment: `strong`
- Why: clean placement + two successful attacks + territorial gain; fortify was unavailable
- Rubric result: `4.40 / 5`, `strong`
- Verdict: acceptable
- Note: the lower `plan_alignment` score for missing fortify is reasonable but should be monitored on live games so the rubric does not punish forced non-fortify turns too aggressively

3. `Round 4, Turn 10, Charlie`
- Manual judgment: `strong`
- Why: card trade converted into a stronger attack turn with clear board improvement
- Rubric result: `4.40 / 5`, `strong`
- Verdict: acceptable
- Note: the rubric correctly avoided overrewarding the turn despite a large troop swing from the trade-in

4. `Round 5, Turn 13, Charlie`
- Manual judgment: `strong but lighter`
- Why: one clean successful attack and modest positional gain, but less complete than earlier turns
- Rubric result: `4.20 / 5`, `strong`
- Verdict: acceptable
- Note: this is near the lower edge of the `strong` band and feels correctly placed

## Weak-Turn Check
The scripted sample did not naturally produce weak turns because the scripted agents execute legal moves cleanly. Weak-turn separation is therefore also covered by the explicit regression fixture in:

- [test_strategic_rubric.py](../tests/test_strategic_rubric.py)

That fixture verifies that:
- missing/empty plans
- invalid actions
- random fallback behavior
- territorial loss
- continent loss

are scored into the `weak` range.

## Calibration Result
No rubric-weight changes were made after this first pass.

Reason:
- the reviewed strong turns were scored as strong for the right reasons
- the lower-alignment cases landed below the fully coherent turns without dropping out of the strong band
- existing weak-fixture coverage already showed the rubric can separate obvious low-quality turns

## Remaining Risk
This initial calibration is useful but not sufficient for live conclusions because scripted agents are cleaner and more internally consistent than real LLM turns.

The next calibration pass should use:
- real LLM games
- at least one sample each of `strong`, `mixed`, and `weak` turns
- special attention to:
  - overcautious skip turns
  - invalid retry loops
  - lucky tactical wins with poor plans
  - good plans that fail because of combat variance
