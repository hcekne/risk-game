# Cross-Provider Frontier Strategic Full 16: Invalid Trial

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `frontier_strategic_full_16`
- Raw local artifacts: `/shared-game-results/experiments/experiment__2026-05-04_11-33-15__frontier_strategic_full_16`
- Status: invalid

## Why This Trial Is Invalid

This batch should not be used as a research result.

Two independent issues contaminated it:

1. **Initial troop placement parser bug**
   - single-move setup responses could contain more than one `|||Territory, 1|||` block
   - the phase-0 validator accepted the turn based on the first parsed move
   - the engine then applied all parsed moves
   - this eventually surfaced as:
     - `gemini-3.1-pro-preview has 31 troops`
     - `ValueError: Invalid territory assignment`

2. **OpenAI quota exhaustion**
   - OpenAI `429 insufficient_quota` failures begin in game `9`
   - they continue heavily in games `10` and the failed game `11`
   - this contaminated the OpenAI side of the batch independently of the setup bug

Because the placement-parser issue already appears before game `9`, excluding only the later quota-contaminated games would still leave setup-corrupted results in the retained subset.

## What Was Observed Before Invalidation

The batch recorded `10` completed games before the crash:

- `gemini-3.1-pro-preview`: `4` wins
- `gpt-5.1`: `3`
- `claude-opus-4-7`: `2`
- `kimi-k2.6`: `1`

Those counts are descriptive only and should not be treated as valid experiment outcomes.

## Root Cause Summary

The setup bug was fixed after this run by making single-move phases parse only one explicit move block and by hardening initial-placement validation to reject multi-move payloads.

The relevant fix was applied in:

- `risk_game/player_agent.py`
- `risk_game/game_master.py`
- `tests/test_player_agent.py`

## Decision

Treat `/shared-game-results/experiments/experiment__2026-05-04_11-33-15__frontier_strategic_full_16` as an **invalid** trial.

Do not include it in provider comparisons, summaries, or rankings.

Rerun the strategic cross-provider batch from scratch after:

- the parser fix
- replenished OpenAI credits/quota
- adequate Gemini quota
