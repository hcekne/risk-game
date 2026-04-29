# Experiment Suites

This folder stores the tracked, human-written research record for scored experiment programs.

Use this layer for:
- suite-level goals and scope
- locked protocol notes
- finished experiment analyses
- cross-experiment comparisons
- analyst/researcher workflow notes

Do not use this layer for:
- raw runtime artifacts
- prompt/response logs
- per-turn CSVs
- generated JSON summaries

Those runtime artifacts belong under `game_results/experiments/...` and remain git-ignored by default.

## Recommended Structure

Each suite should have its own folder, for example:

```text
docs/experiment-suites/2026-q2-strategic-tests/
```

Inside each suite folder:
- `README.md`: suite scope, protocol, current registry, and status
- one Markdown file per completed experiment
- optional methodology notes if a suite needs special handling

## Required Contents For A Completed Experiment Write-Up

Each tracked experiment analysis should include:
- experiment label and raw artifact path
- lineup and settings
- exact `H0` and `H1`
- primary metric
- statistical method
- result
- interpretation
- operational caveats
- next-step recommendation

## Recommended Workflow

1. Run the batch with `scripts/run_experiment.py`.
2. Keep the raw local artifacts under `game_results/experiments/experiment__...`.
3. Analyze the finished batch from `experiment_manifest.json`, `experiment_results.json`, `experiment_summary.json`, and any targeted `llm_interactions/...` logs.
4. Write the durable experiment note in the relevant suite folder under `docs/experiment-suites/...`.
5. Add the experiment to the suite registry in that suite's `README.md`.

## Contribution Rule

If a new scored experiment is important enough to cite in the article or use for model comparisons, it should have:
- a complete raw artifact folder under `game_results/experiments/...`
- a tracked Markdown analysis under `docs/experiment-suites/...`
