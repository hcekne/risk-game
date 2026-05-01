# Strategic Analysis Workflow

## Purpose
This repo now treats strategic analysis as a first-class experiment artifact rather than something inferred manually from board CSVs after the fact.

The goal is to answer a narrower but defensible question:

- How strategic does an agent's play look from its observable turn-by-turn behavior?

This is intentionally narrower than "what was the model secretly thinking internally."

## Key Method Decision
We do **not** claim to measure hidden provider chain-of-thought.

Instead, we analyze **observable strategic traces**:
- the pre-turn plan the agent declares
- the short reasons it gives for concrete moves
- the exact actions it attempts
- whether those actions are valid
- what those actions actually changed on the board

That keeps the analysis grounded in artifacts we can reproduce and compare across providers.

## Saved Artifacts
Each full game run now saves:

- `game_state_turn_N.csv`
- `player_data_turn_N.csv`
- `turn_summary_turn_N.json`
- `end_game_results.json`

The new `turn_summary_turn_N.json` files are the main reasoning-analysis artifact. Each one contains:
- pre-turn player state
- pre-turn all-player snapshot
- declared turn plan
- per-phase events for card trade, placement, attack, and fortify
- raw prompt response when available
- legality and retry/fallback information
- post-turn player state
- post-turn all-player snapshot
- derived outcome metrics for that turn

## Strategic Rubric
The current rubric is heuristic and intentionally observable-only. It scores each turn on five dimensions from `0` to `5`:

1. `plan_concreteness`
- Did the agent provide a non-empty plan?
- Was it specific enough to mention clear intents or concrete targets?

2. `action_validity`
- Did the agent stay within the legal move space?
- Did it require retries or random fallback logic?

3. `plan_alignment`
- Did the executed moves match the declared plan?
- If the plan named territories or continents, did those show up in actual actions?

4. `tactical_efficiency`
- Did attacks resolve efficiently?
- Did the agent convert tactical opportunities into successful territorial gains rather than wasted fights?

5. `positional_outcome`
- Did the turn improve the board state?
- Territory gain, continent gain, card gain, and distance-to-win all matter here.

The overall turn score is the simple average of those five dimensions.

Banding:
- `strong`: `>= 4.2`
- `mixed`: `>= 3.0` and `< 4.2`
- `weak`: `< 3.0`

## Why This Rubric Exists
This rubric is meant to support three concrete workflows:

1. Compare prompt packs and state representations.
2. Compare models and reasoning modes on something richer than win rate.
3. Identify where an agent is failing:
- no plan
- plan/action mismatch
- invalid moves
- tactically bad attacks
- position worsens despite coherent-looking language

## Current Limitations
Important caveats:

- The rubric is heuristic, not ground truth.
- A short plan can still be strategically strong.
- Some strategically correct moves are intentionally low-action, so restraint should not be scored as passivity by default.
- Different models vary in how much they verbalize intent, so plan quality scores should not be overinterpreted alone.
- A lucky combat roll can improve `positional_outcome` even if the plan was mediocre.

Because of that, the rubric should be used together with:
- win/loss results
- territory/time plots
- attack success rates
- invalid move rates
- manual review of a sample of turns

## Commands
Generate a live or scripted game as usual, then analyze a saved game folder:

```bash
docker compose exec -T risk-game python /app/scripts/analyze_turn_summaries.py \
  --game-folder /shared-game-results/game__YYYY-MM-DD_HH-MM-SS
```

Outputs:
- `strategic_analysis.md`
- `strategic_metrics.json`
- `strategic_turn_scores.json`

## Intended Next Iteration
The next improvement should be rubric calibration rather than adding more scoring complexity immediately.

Recommended follow-up:
- manually review a sample of turns
- compare human judgments to rubric scores
- adjust the heuristics only after seeing systematic disagreement
- then benchmark the rubric across prompt packs, state formats, and model families
