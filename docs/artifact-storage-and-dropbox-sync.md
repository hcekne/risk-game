# Artifact Storage And Dropbox Sync

## Purpose
This note defines the canonical cross-machine workflow for this repo:
- Git for code, docs, configs, and tracked analyses
- Dropbox bundle snapshots for runtime `game_results`

It also records:
- where runtime artifacts live on the current machine
- which experiments and probes already exist
- how to resume work on another laptop or remote server

## Canonical Storage Model

### Git-Tracked Repo
Current repo root on this machine:

```text
/home/hcekne/repos/risk-game
```

Git should contain:
- source code
- configs
- prompt and system-prompt definitions
- tracked experiment write-ups under `docs/experiment-suites/...`
- helper scripts

Git should not contain:
- raw experiment outputs
- prompt/response logs
- generated summaries from live runs

### Shared Runtime Artifact Store
Current host-side shared runtime artifact root:

```text
/home/hcekne/shared/risk-game/game_results
```

Inside the container, that path is mounted at:

```text
/shared-game-results
```

and the standard stack sets:

```text
RISK_GAME_RESULTS_DIR=/shared-game-results
```

Important consequence:
- when the stack is started normally, runtime artifacts are written to the shared store, not the repo-local `game_results/` tree
- the repo-local `game_results/` directory is now mainly tracked scaffolding plus documentation

## Why Bundle Restore Is The Default
For cross-machine handoff, use a compressed bundle, not raw Dropbox tree sync.

Why:
- `game_results` contains thousands of small files
- Dropbox API sync on many tiny files is much slower than a single archive
- machine-to-machine restore is dramatically faster and simpler with a tarball

Use raw `rclone sync` or `bisync` only if you intentionally want a long-lived mirrored artifact tree. Do not treat that as the default migration path.

## Current Local Artifact Layout
Important subfolders under the shared `game_results/` root:
- `experiments/`
  Scored experiment batches and their manifests, summaries, and linked game folders
- `model_probes/`
  One-off and repeated probe outputs, including prompt-architecture probes
- `prompt_smoke_runs/`
  Prompt-smoke qualification runs used before full experiments
- `league_logs/`
  Long-running live experiment logs
- `rubric_calibration/`
  Strategic-rubric calibration outputs
- `analysis_*`
  Post-hoc analysis folders and derived metrics

Tracked long-form analysis notes live under:

```text
/home/hcekne/repos/risk-game/docs/experiment-suites
```

## Short Inventory Of Completed Work

### Scored Experiment Batches

1. OpenAI Mini Reasoning 1
- Type: interrupted diagnostic batch
- Raw artifacts:
  - `/home/hcekne/shared/risk-game/game_results/experiments/experiment__2026-04-27_22-05-54__mini_reasoning_1`
- Notes:
  - useful mainly as an early timing and failure reference
  - not the main result to cite

2. OpenAI Mini Reasoning 2
- Type: completed scored batch
- Raw artifacts:
  - `/home/hcekne/shared/risk-game/game_results/experiments/experiment__2026-04-27_22-29-27__mini_reasoning_2`
- Tracked analysis:
  - [2026-04-27_openai-mini-reasoning.md](experiment-suites/2026-q2-strategic-tests/2026-04-27_openai-mini-reasoning.md)

3. OpenAI Mini High-vs-Medium Recovery
- Type: completed scored batch
- Raw artifacts:
  - `/home/hcekne/shared/risk-game/game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16`
- Tracked analysis:
  - [2026-04-29_openai-mini-high-vs-medium-recovery.md](experiment-suites/2026-q2-strategic-tests/2026-04-29_openai-mini-high-vs-medium-recovery.md)

4. Cross-Provider Frontier Smoke 1
- Type: completed one-game smoke batch
- Raw artifacts:
  - `/home/hcekne/shared/risk-game/game_results/experiments/experiment__2026-04-29_20-44-02__frontier_championship_smoke_1`
- Notes:
  - this is a smoke or pilot result, not a full championship
  - useful for checking viability, turn timing, and provider behavior before the staged cross-provider batch

5. Cross-Provider Frontier Smoke 2
- Type: completed two-game scored smoke batch
- Raw artifacts:
  - `/home/hcekne/shared/risk-game/game_results/experiments/experiment__2026-05-01_09-03-34__frontier_smoke`
- Tracked analysis:
  - [2026-05-01_cross-provider-frontier-smoke.md](experiment-suites/2026-q2-strategic-tests/2026-05-01_cross-provider-frontier-smoke.md)
- Notes:
  - this is still a pilot, not a final cross-provider championship
  - it is the strongest current tracked evidence that `gpt-5.5` is operationally too slow for the standard `90s / 15s` live-turn condition

### Model And Prompt Probes

1. Breakthrough scenario probes
- Raw folder:
  - `/home/hcekne/shared/risk-game/game_results/model_probes/breakthrough_scenarios`
- Important files already created:
  - `gpt-5.4-mini_1777467541.json`
  - `gpt-5.4-mini_1777467879.json`
  - `gpt-5.4-mini_1777471778.json`
  - `gpt-5.4-mini_1777476668.json`
  - `gpt-5.4-mini_1777478452.json`
- Purpose:
  - probe fast attack-chain execution
  - compare prompt architectures such as `minimal_baseline`, `system_prompt_only`, `system_plus_execution_handoff`, and `full_live`

2. Provider and model viability probes
- Raw folder:
  - `/home/hcekne/shared/risk-game/game_results/model_probes`
- Examples:
  - `gpt41_initial_probe_2026-04-27.json`
  - `gpt55pro_initial_probe_2026-04-27.json`
  - `gpt55pro_capital_repeats_2026-04-27.json`
  - `openai_control_initial_probe_2026-04-27.json`
  - `live_turn_setting_probes/.../live_turn_setting_probe_results.json`
  - `anthropic_thinking_viability/.../anthropic_opus_47_thinking_probe.json`

3. Prompt-smoke qualification runs
- Raw folder:
  - `/home/hcekne/shared/risk-game/game_results/prompt_smoke_runs`

## Recommended Dropbox Layout
Use a shared Dropbox folder like:

```text
risk-game-shared/
  bundles/
    latest_game_results.tar.gz
    latest_game_results.manifest.txt
    risk-game_game-results_<timestamp>.tar.gz
    risk-game_game-results_<timestamp>.manifest.txt
```

Optional long-lived raw mirror:

```text
risk-game-shared/game_results/
```

That raw mirror is optional. The bundle snapshot path above is the canonical migration path.

## One-Time rclone Setup Per Machine

### 1. Start The Stack
From the repo root:

```bash
bash start_container.sh
```

### 2. Configure Dropbox OAuth
Use the helper from the host:

```bash
bash scripts/rclone_config_host_network.sh
```

For a local machine with a browser, normal auto-config is fine.

For a remote server, use one of these:
- SSH tunnel, then answer `y` to auto-config
- headless/manual flow, then answer `n`

Recommended server tunnel:

```bash
ssh -L 53682:127.0.0.1:53682 <user>@<server>
```

Then, on the server in that tunneled session:

```bash
cd ~/repos/risk-game
bash scripts/rclone_config_host_network.sh
```

When using a custom Dropbox app, make sure its redirect URI includes:

```text
http://localhost:53682/
```

### 3. Verify The Remote
Inside the app container:

```bash
docker exec -it risk-game-container bash
rclone lsd dropbox:
```

Expected shape:

```text
          -1 ... risk-game-shared
```

## Canonical Machine-To-Machine Workflow

### Source Machine: Create And Upload A Fresh Bundle
From the repo root:

```bash
bash scripts/upload_game_results_bundle.sh
```

Optional labeled snapshot:

```bash
bash scripts/upload_game_results_bundle.sh frontier_stage1
```

What this does:
- archives `/shared-game-results`
- uploads a timestamped tarball and manifest
- refreshes:
  - `dropbox:risk-game-shared/bundles/latest_game_results.tar.gz`
  - `dropbox:risk-game-shared/bundles/latest_game_results.manifest.txt`

### Target Machine: Restore The Latest Bundle
From the repo root:

```bash
bash scripts/restore_game_results_bundle.sh dropbox:risk-game-shared/bundles latest_game_results.tar.gz --force
```

What `--force` does:
- clears the target machine's existing `/shared-game-results`
- restores the snapshot into that location

Do not manually clear the source machine's shared store before bundling. The source shared store is the artifact source of truth.

### Verify The Restore
Inside the container:

```bash
echo "$RISK_GAME_RESULTS_DIR"
ls -la /shared-game-results/experiments | head -20
ls -la /shared-game-results/model_probes | head -20
```

Then run one known summary:

```bash
docker exec -it risk-game-container bash -lc 'cd /app && python scripts/experiment_summary.py --experiment-folder /shared-game-results/experiments/experiment__2026-04-29_20-44-02__frontier_championship_smoke_1'
```

If that prints the expected summary, the restore worked.

## Optional Raw Mirror Workflow
These helpers still exist:

```bash
bash scripts/bootstrap_shared_game_results.sh
bash scripts/rclone_pull_shared_game_results.sh
bash scripts/rclone_push_shared_game_results.sh
bash scripts/rclone_bisync_shared_game_results.sh --resync
```

Use them only if you intentionally want a live Dropbox mirror of the raw tree. For migration and resumption, prefer the bundle scripts instead:

```bash
bash scripts/create_game_results_bundle.sh
bash scripts/upload_game_results_bundle.sh
bash scripts/download_game_results_bundle.sh
bash scripts/restore_game_results_bundle.sh
```

## Resume Checklist On Another Machine
1. `git clone` or `git pull`
2. `bash start_container.sh`
3. `bash scripts/rclone_config_host_network.sh`
4. `bash scripts/restore_game_results_bundle.sh dropbox:risk-game-shared/bundles latest_game_results.tar.gz --force`
5. verify one known experiment summary
6. continue running probes or experiments

That is the canonical handoff workflow for this repo.
