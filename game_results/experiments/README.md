# Experiment Folders

Runtime experiment batches created by `scripts/run_experiment.py` are written here.

Expected structure:

```text
game_results/experiments/experiment__YYYY-MM-DD_HH-MM-SS__<label>/
  experiment_manifest.json
  experiment_status.json
  experiment_results.json
  experiment_summary.json
  experiment_summary.md
  preflight_results.json
  experiment_failure.json
  game__YYYY-MM-DD_HH-MM-SS/
  llm_interactions/
```

Notes:
- The folder structure is tracked in git so agents and humans have a stable place to look.
- Runtime experiment files themselves are ignored by git.
- Use `scripts/experiment_status.py` and `scripts/experiment_summary.py` instead of reading raw logs when possible.
- Durable tracked write-ups belong under `docs/experiment-suites/...`, not in this folder.
- For a short inventory of completed local experiments and the Dropbox sync plan for moving these folders between machines, see [docs/artifact-storage-and-dropbox-sync.md](/home/hcekne/repos/risk-game/docs/artifact-storage-and-dropbox-sync.md).
