# Cross-Provider Frontier Championship: Staged Run Plan

## Purpose
This is the first staged run plan for the 2026-Q2 cross-provider frontier championship.

The locked roster is:
- `gpt-5.5`
- `claude-opus-4-7`
- `gemini-3.1-pro-preview`
- `kimi-k2.6`

The exact frozen agent spec lives in:
- [configs/experiments/2026_q2_cross_provider_frontier.json](/home/hcekne/repos/risk-game/configs/experiments/2026_q2_cross_provider_frontier.json:1)

## Timing Policy
Use normal live-turn timing:
- `90s` full turn timer
- `15s` placement timer

Rationale:
- this keeps the championship under realistic synchronous game conditions
- all four selected models have already cleared the live-turn prompt smoke tests under this general regime
- the earlier `high`-reasoning timing investigations were specific to a different OpenAI reasoning experiment and should not be carried over here

## Staged Execution
The full headline batch is `16` games.

Why `16`:
- with `4` players and cyclic seat rotation, `16` games gives each model each seat exactly `4` times

To fit travel constraints, run the batch in two stages:

### Stage 1: Run 4 Games Now
This gives each model each seat exactly once and serves as the operational pilot.

```bash
make run-experiment ARGS="--label frontier_championship_stage1_4 --agent-specs-file configs/experiments/2026_q2_cross_provider_frontier.json --num-games 4 --turn-time-limit-seconds 90 --placement-time-limit-seconds 15"
```

### Stage 2: Run 12 Games Later
This completes the full `16`-game championship.

```bash
make run-experiment ARGS="--label frontier_championship_stage2_12 --agent-specs-file configs/experiments/2026_q2_cross_provider_frontier.json --num-games 12 --turn-time-limit-seconds 90 --placement-time-limit-seconds 15"
```

## Combine The Two Stages
After both stages finish, combine them into one staged-series summary.

Replace the experiment-folder paths below with the actual stage folders that were created under `game_results/experiments/`.

```bash
make experiment-series-summary ARGS="--label 2026_q2_cross_provider_frontier --experiment-folders game_results/experiments/experiment__STAGE1_FOLDER game_results/experiments/experiment__STAGE2_FOLDER"
```

This writes the combined series output under:
- `game_results/experiment_series/2026_q2_cross_provider_frontier/`

Artifacts:
- `series_manifest.json`
- `series_results.json`
- `series_summary.json`
- `series_summary.md`

## Interpretation Policy
- Treat the first `4` games as a staged pilot plus the first seat-balanced quarter of the championship.
- Do not over-interpret the stage-1 result on its own.
- Use the combined `16`-game series as the actual research-facing cross-provider championship result.
