# Artifact Storage And Dropbox Sync

## Purpose
This note records:
- which experiments and probes have already been run
- where their artifacts live on the current machine
- a practical plan for syncing those artifacts to a shared Dropbox folder so work can continue from another machine or remote server

Current repo root on this machine:
```text
/home/hcekne/repos/risk-game
```

Current shared runtime artifact root on this machine:
```text
/home/hcekne/shared/risk-game/game_results
```

## Local Artifact Layout
The repo is now split into two persistence layers:

1. Git-tracked code, configs, docs, and analysis notes
```text
/home/hcekne/repos/risk-game
```

2. Shared generated runtime artifacts
```text
/home/hcekne/shared/risk-game/game_results
```

Inside the container, the shared host path is mounted at:
```text
/shared-game-results
```

and runtime writers resolve:
```text
RISK_GAME_RESULTS_DIR=/shared-game-results
```

Important subfolders under the shared `game_results/` root:
- `experiments/`
  Scored experiment batches and their per-batch manifests, summaries, and linked game folders.
- `model_probes/`
  One-off and repeated probe outputs, including prompt-architecture probes and provider latency/behavior probes.
- `prompt_smoke_runs/`
  Prompt-smoke qualification runs used to verify model viability before full experiments.
- `league_logs/`
  Long-running live experiment logs.
- `rubric_calibration/`
  Strategic-rubric calibration outputs.
- `analysis_*`
  Post-hoc analysis folders such as plots and derived metrics.

Tracked long-form analysis notes live in:
```text
/home/hcekne/repos/risk-game/docs/experiment-suites
```

## Short Inventory Of Completed Work

### Scored Experiment Batches

1. OpenAI Mini Reasoning 1
- Type: interrupted diagnostic batch
- Local artifacts:
  - `/home/hcekne/repos/risk-game/game_results/experiments/experiment__2026-04-27_22-05-54__mini_reasoning_1`
- Notes:
  - useful mainly as an early failure/timing reference
  - not the main result to cite

2. OpenAI Mini Reasoning 2
- Type: completed scored batch
- Local artifacts:
  - `/home/hcekne/repos/risk-game/game_results/experiments/experiment__2026-04-27_22-29-27__mini_reasoning_2`
- Tracked analysis:
  - [2026-04-27_openai-mini-reasoning.md](experiment-suites/2026-q2-strategic-tests/2026-04-27_openai-mini-reasoning.md)

3. OpenAI Mini High-vs-Medium Recovery
- Type: completed scored batch
- Local artifacts:
  - `/home/hcekne/repos/risk-game/game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16`
- Tracked analysis:
  - [2026-04-29_openai-mini-high-vs-medium-recovery.md](experiment-suites/2026-q2-strategic-tests/2026-04-29_openai-mini-high-vs-medium-recovery.md)

4. Cross-Provider Frontier Smoke 1
- Type: completed one-game smoke batch
- Local artifacts:
  - `/home/hcekne/repos/risk-game/game_results/experiments/experiment__2026-04-29_20-44-02__frontier_championship_smoke_1`
- Notes:
  - this is a smoke/pilot result, not a full championship
  - it is useful for checking viability, turn timing, and provider behavior before the staged 16-game championship

### Model / Prompt Probes

1. Breakthrough scenario probes
- Local folder:
  - `/home/hcekne/repos/risk-game/game_results/model_probes/breakthrough_scenarios`
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
- Local folder:
  - `/home/hcekne/repos/risk-game/game_results/model_probes`
- Examples:
  - `gpt41_initial_probe_2026-04-27.json`
  - `gpt55pro_initial_probe_2026-04-27.json`
  - `gpt55pro_capital_repeats_2026-04-27.json`
  - `openai_control_initial_probe_2026-04-27.json`
  - `live_turn_setting_probes/.../live_turn_setting_probe_results.json`
  - `anthropic_thinking_viability/.../anthropic_opus_47_thinking_probe.json`

3. Prompt-smoke qualification runs
- Local folder:
  - `/home/hcekne/repos/risk-game/game_results/prompt_smoke_runs`

### Other Useful Local Artifacts
- League logs:
  - `/home/hcekne/repos/risk-game/game_results/league_logs`
- Rubric calibration:
  - `/home/hcekne/repos/risk-game/game_results/rubric_calibration`
- Earlier standalone analysis:
  - `/home/hcekne/repos/risk-game/game_results/analysis_nano_medium_full_initial_2026-04-22`

## What Should Be Synced To Dropbox

Recommended to sync:
- `game_results/experiments/`
- `game_results/model_probes/`
- `game_results/prompt_smoke_runs/`
- `game_results/league_logs/`
- `game_results/rubric_calibration/`
- `game_results/analysis_*`

Optional to sync:
- `game_results/llm_interactions/`
  Only if you explicitly want the raw full prompt/response logs available on other machines. These can be large.

Do **not** sync:
- `.env`
- `.venv/`
- Docker images / local Docker volumes
- `data/qdrant/`
- any provider secrets

## Recommended Dropbox Layout

Use a shared Dropbox folder named something like:
```text
risk-game-shared
```

Recommended structure inside Dropbox:
```text
risk-game-shared/
  game_results/
    experiments/
    experiment_series/
    model_probes/
    prompt_smoke_runs/
    league_logs/
    rubric_calibration/
    analysis/
  notes/
    machine_state/
```

This keeps generated artifacts separate from the git repo itself. The code and docs should continue to move through Git; the large generated outputs should move through Dropbox.

## Recommended Sync Method

For a headless server or remote machine, the cleanest option is `rclone` with Dropbox.

Why `rclone`:
- works well on servers
- works without a desktop Dropbox client
- easy to script
- easy to use from multiple machines

## Dropbox Sync Plan

## Shared Runtime Layout

The preferred architecture is now:
- git-tracked repo contents under `/home/hcekne/repos/risk-game`
- runtime artifacts under `/home/hcekne/shared/risk-game/game_results`

This avoids duplicating large experiment trees across multiple checkouts.

On a new machine:
1. clone the repo anywhere you want
2. set `GAME_RESULTS_HOST_PATH` if you do not want the default
3. start the container
4. pull or bisync the shared artifact tree

## Container-First `rclone` Setup

The repo now supports running `rclone` directly inside the `risk-game` container.

Container-persistent paths:
- rclone config:
  - `/home/<user>/.config/rclone`
- rclone cache:
  - `/home/<user>/.cache/rclone`

These are bind-mounted to project-local folders on the host:
- `/home/hcekne/repos/risk-game/data/rclone-config`
- `/home/hcekne/repos/risk-game/data/rclone-cache`

That means:
- your `rclone` configuration survives container restarts and rebuilds
- your Dropbox remote only needs to be configured once per machine

### Rebuild The Container After This Change
From the host:
```bash
docker-compose up --build -d
```

Then enter the container:
```bash
docker exec -it risk-game-container bash
```

Verify `rclone` is available:
```bash
rclone version
```

The host-side shared artifact path defaults to:
```bash
$HOME/shared/risk-game/game_results
```

You can override it before starting the stack:
```bash
export GAME_RESULTS_HOST_PATH=/some/other/path/game_results
```

### 1. Set Up `rclone` Once Per Machine
Do **not** do Dropbox auto-config from a normal `docker exec` shell inside the long-running app container. If you choose auto config there, the callback URL points at the container's own `127.0.0.1`, which your host browser cannot reach.

Instead, use the helper below from the host. It launches the same image with `--network host` and writes the config into the persistent mounted folders:
```bash
bash scripts/rclone_config_host_network.sh
```

If you are already inside `rclone config` in the app container and chose auto config, abort it and rerun the helper above.

Create a Dropbox remote, for example:
```text
dropbox
```

Inside the container, that configuration will be written under:
```text
/home/<user>/.config/rclone/rclone.conf
```

Because of the bind mount, the real host-side file will live under:
```text
/home/hcekne/repos/risk-game/data/rclone-config/
```

### 2. Create The Shared Folder
After the helper finishes, use the normal app container again:
```bash
docker exec -it risk-game-container bash
```

Create the destination once:
```bash
rclone mkdir dropbox:risk-game-shared
```

### 3. Upload Current Local Artifacts
For the shared-layout workflow, prefer these host-side helpers:

Bootstrap the shared host folder from the current repo-local artifact tree:
```bash
bash scripts/bootstrap_shared_game_results.sh
```

Push local shared artifacts to Dropbox:
```bash
bash scripts/rclone_push_shared_game_results.sh
```

Pull shared artifacts down from Dropbox:
```bash
bash scripts/rclone_pull_shared_game_results.sh
```

Bidirectional sync:
```bash
bash scripts/rclone_bisync_shared_game_results.sh --resync
```

After the first `--resync`, use:
```bash
bash scripts/rclone_bisync_shared_game_results.sh
```

From inside the container, you can still run raw `rclone` commands or the older selective helper script.

Helper script:
```bash
bash scripts/sync_artifacts_to_rclone.sh
```

Optional custom remote path:
```bash
bash scripts/sync_artifacts_to_rclone.sh dropbox:risk-game-shared/game_results
```

Equivalent raw `rclone` commands:

```bash
rclone copy /home/hcekne/repos/risk-game/game_results/experiments dropbox:risk-game-shared/game_results/experiments --progress
rclone copy /home/hcekne/repos/risk-game/game_results/model_probes dropbox:risk-game-shared/game_results/model_probes --progress
rclone copy /home/hcekne/repos/risk-game/game_results/prompt_smoke_runs dropbox:risk-game-shared/game_results/prompt_smoke_runs --progress
rclone copy /home/hcekne/repos/risk-game/game_results/league_logs dropbox:risk-game-shared/game_results/league_logs --progress
rclone copy /home/hcekne/repos/risk-game/game_results/rubric_calibration dropbox:risk-game-shared/game_results/rubric_calibration --progress
```

If you want the additional analysis folder too:
```bash
rclone copy /home/hcekne/repos/risk-game/game_results/analysis_nano_medium_full_initial_2026-04-22 dropbox:risk-game-shared/game_results/analysis/analysis_nano_medium_full_initial_2026-04-22 --progress
```

Use `copy`, not `sync`, unless you explicitly want Dropbox to exactly mirror the local machine and delete remote files that are missing locally.

### 4. Rehydrate On Another Machine
On the new machine:

1. Clone the repo:
```bash
git clone git@github.com:hcekne/risk-game.git
cd risk-game
```

2. Start the container:
```bash
./start_container.sh
```

3. Pull the shared artifacts back into the shared host path:
Preferred:
```bash
bash scripts/rclone_pull_shared_game_results.sh
```

or bidirectional:
```bash
bash scripts/rclone_bisync_shared_game_results.sh --resync
```

Inside the rebuilt container, you can still use the older selective restore script if needed:
```bash
bash scripts/restore_artifacts_from_rclone.sh
```

Equivalent raw commands:
```bash
rclone copy dropbox:risk-game-shared/game_results/experiments /home/YOUR_USER/repos/risk-game/game_results/experiments --progress
rclone copy dropbox:risk-game-shared/game_results/model_probes /home/YOUR_USER/repos/risk-game/game_results/model_probes --progress
rclone copy dropbox:risk-game-shared/game_results/prompt_smoke_runs /home/YOUR_USER/repos/risk-game/game_results/prompt_smoke_runs --progress
rclone copy dropbox:risk-game-shared/game_results/league_logs /home/YOUR_USER/repos/risk-game/game_results/league_logs --progress
rclone copy dropbox:risk-game-shared/game_results/rubric_calibration /home/YOUR_USER/repos/risk-game/game_results/rubric_calibration --progress
```

4. Recreate `.env` locally on that machine.

### 5. Resume Checklist
On the new machine, before resuming work:
- confirm the git checkout is on the expected branch/commit
- confirm the shared host artifact path contains the already-run batches
- confirm `experiments/` contains the already-run batches
- confirm `model_probes/` contains the latest probe outputs
- inspect the latest batch summary with:
```bash
make experiment-summary
```
- inspect the suite docs under:
```text
docs/experiment-suites/2026-q2-strategic-tests/
```

## Recommended Ongoing Practice

After each major run:
1. push code/docs to Git
2. `bash scripts/rclone_bisync_shared_game_results.sh`
3. do not rely on Git alone for generated outputs

This gives the cleanest split:
- Git for code, configs, docs, tracked analysis
- Dropbox for heavy generated experiment outputs
