# Risk Game AI

## Provider Update 26.04.2026 ##

The repo now supports current explicit model IDs across:
- OpenAI
- Anthropic
- Gemini
- Moonshot / Kimi

Preferred practice is to use explicit provider model strings in experiments rather than numeric selectors.

The current supported provider/model surface is documented in [docs/provider-models.md](docs/provider-models.md).

## Overview
This project implements a simplified version of the Risk board game with AI players.

The AI players play against each other using the API of the respective LLMs.



## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/hcekne/risk-game.git
   cd risk-game
   ```

2. **Add API keys to .env file:**

   Set the values of the  API to match your own
   Copy the sample environment file
   ```bash
   cp .env_example .env
   ```
   Edit the .env file and insert your own keys
   ```bash
   nano .env
   ```

   Provider keys currently supported by the repo:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY` or `GOOGLE_API_KEY`
   - `MOONSHOT_API_KEY`


3. **Create the dev container to run the code:**
   ```bash
   ./start_container.sh
   ```
4. **Enter into the container:**
   ```bash
   docker exec -it risk-game-container bash
   ```

## Standard Dev Workflow
This repo uses container-first development as the standard workflow for humans and coding agents.

Preferred commands:
```bash
make up
make shell
make test
make test-live
make test-live-canary
make test-live-canary-gemini
make test-live-canary-moonshot
make run-example
make down
```

If you are using Claude, Gemini, Codex, or another coding agent, see [AGENTS.md](AGENTS.md). The container workflow in that file is the canonical way to work on this repo.

The `risk-game` container is a dev/runtime container and does not need a published app port. The only host-exposed service required by default is `qdrant` on `6333`.
The container image now includes `make` and `sudo` as standard utilities.
The container image now also includes `rclone`, and its config/cache directories are bind-mounted into `data/rclone-config` and `data/rclone-cache` so Dropbox sync setup survives rebuilds.

## Running the Game
To run the game, execute the following command inside the container:
```bash
python scripts/example_run.py
```

You can also run it from the host through Docker:
```bash
make run-example
```

The default example run now uses a 4-player `gpt-5.4-mini` reasoning arena:
- `gpt-5.4-mini-none`
- `gpt-5.4-mini-low`
- `gpt-5.4-mini-medium`
- `gpt-5.4-mini-high`

This is the default reasoning-ladder setup for live OpenAI testing in this repo.

## Provider Model Options
The experiment layer now supports either legacy numeric selectors or explicit provider model IDs.

Preferred usage is explicit model IDs, for example:
```python
from risk_game.experiments import (
    AgentSpec,
    Experiment,
    build_live_turn_frontier_roster,
)
from risk_game.game_config import GameConfig

experiment = Experiment(
    GameConfig(progressive=True, capitals=False, max_rounds=10),
    num_games=3,
    agent_specs=build_live_turn_frontier_roster(),
)
```

`build_live_turn_frontier_roster()` is the current locked cross-provider live-turn roster:
- OpenAI: `gpt-5.5` with `reasoning_effort="medium"`
- Anthropic: `claude-opus-4-7` in standard mode (`enable_thinking=False`)
- Google: `gemini-3.1-pro-preview`
- Moonshot: `kimi-k2.6` with thinking disabled

Current core provider coverage:
- OpenAI: `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.4-pro`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `gpt-5.1`, `gpt-5.2`, `gpt-5.2-pro`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o3-mini`, `o3-pro`, `o4-mini`
- Anthropic: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-opus-4-5-20251101`, `claude-haiku-4-5-20251001`, `claude-sonnet-4-5-20250929`, `claude-opus-4-1-20250805`, `claude-opus-4-20250514`, `claude-sonnet-4-20250514`
- Gemini: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-3-pro-preview`, `gemini-3-flash-preview`, `gemini-3.1-pro-preview`, `gemini-3.1-flash-lite-preview`
- Moonshot: `kimi-k2.6`, `kimi-k2.5`, `moonshot-v1-auto`, `moonshot-v1-8k`, `moonshot-v1-32k`, `moonshot-v1-128k`

See [docs/provider-models.md](docs/provider-models.md) for live-account snapshots, support notes, and provider-specific reasoning/thinking behavior.
See [docs/development-log.md](docs/development-log.md) for the running record of major experiment decisions, model viability findings, and architecture direction.
See [docs/experiment-program.md](docs/experiment-program.md) for the current planned experiment series, hypotheses, seat-rotation policy, and sample sizes.
See [docs/experiment-suites/README.md](docs/experiment-suites/README.md) for the tracked experiment-suite archive, including completed analyses and how to add future scored runs.
See [docs/experiment-suites/2026-q2-strategic-tests/README.md](docs/experiment-suites/2026-q2-strategic-tests/README.md) for the current 2026 Q2 strategic-test suite.
See [docs/artifact-storage-and-dropbox-sync.md](docs/artifact-storage-and-dropbox-sync.md) for a short inventory of completed experiments, the local folder structure on the current machine, and the recommended Dropbox sync plan for resuming from another machine.
For Dropbox OAuth inside Docker, use [scripts/rclone_config_host_network.sh](scripts/rclone_config_host_network.sh) from the host rather than running `rclone config` from a normal `docker exec` shell.

## Shared Artifacts
Runtime experiment output is now designed to live outside the git checkout.

Default host-side shared path:
```bash
$HOME/shared/risk-game/game_results
```

The container mounts that host path at:
```bash
/shared-game-results
```

and all runtime writers now resolve `RISK_GAME_RESULTS_DIR=/shared-game-results`.

This means:
- git repos can be cloned on multiple machines without duplicating large artifact trees
- multiple checkouts can point at the same shared `game_results` store
- Dropbox sync can operate on the shared store directly instead of per-repo copies

Useful helpers:
```bash
bash scripts/bootstrap_shared_game_results.sh
bash scripts/rclone_pull_shared_game_results.sh
bash scripts/rclone_push_shared_game_results.sh
bash scripts/rclone_bisync_shared_game_results.sh --resync
```

## Running Tests
To run the tests inside the container, use the following command:
```bash
pytest tests/
```

Or from the host through Docker:
```bash
make test
```

`make test` runs the deterministic regression suite in-container. Live provider/API checks are separate:
```bash
make test-live
```

For provider canaries, run:
```bash
make test-live-canary
```

That runs the tiny positive paid checks for OpenAI, Gemini, and Moonshot. Provider-specific commands are also available:
```bash
make test-live-canary-openai
make test-live-canary-gemini
make test-live-canary-moonshot
```

The Gemini and Moonshot canaries both ask `What is the capital of Norway? Reply with exactly one word.` and expect `Oslo`.

Testing strategy notes live in [tests/README.md](tests/README.md).

## Strategic Analysis
Saved games now include per-turn strategic traces in `turn_summary_turn_N.json`.

These traces are designed to evaluate **observable strategy**, not hidden chain-of-thought. The repo records:
- pre-turn plan
- action-by-action reasons
- legality / retry behavior
- board-state deltas after the turn

You can turn a saved game folder into a strategic report with:
```bash
docker-compose exec -T risk-game python /app/scripts/analyze_turn_summaries.py \
  --game-folder /app/game_results/game__YYYY-MM-DD_HH-MM-SS
```

That produces:
- `strategic_analysis.md`
- `strategic_metrics.json`
- `strategic_turn_scores.json`

The scoring rubric and the design decisions behind it are documented in [docs/strategic-analysis.md](docs/strategic-analysis.md).
The first manual calibration pass is documented in [docs/strategic-rubric-calibration.md](docs/strategic-rubric-calibration.md).

## LLM Interaction Logs
Live runs now also write full prompt/response interaction logs under:
```text
game_results/llm_interactions/<game_name>/<player>/round_<NN>/<scope or turn>/
```

Each JSON file records:
- full prompt text
- raw model response
- provider and model metadata
- stable `interaction_index` for linking prompt logs back to turn events
- timeout and reasoning settings used for that call
- fallback status
- raw provider error text if the API call failed

Saved games now also include a `game_manifest.json` per run with:
- rules and timer settings
- player roster
- provider/model assignments
- per-phase reasoning profiles

Taken together, `game_manifest.json`, `turn_summary_turn_N.json`, and `llm_interactions/...` are the main retroactive-analysis artifacts. The folder structure is tracked in git, but the runtime log files themselves are ignored.

To replay one saved prompt against live models and compare latency, fallback behavior, and parser validity, use:
```bash
docker-compose exec -T risk-game python /app/scripts/probe_saved_prompt.py \
  --prompt-json /app/game_results/llm_interactions/<game_name>/<player>/round_<NN>/<scope>/0001_initial_troop_placement.json \
  --models gpt-5.5-pro gpt-5.5 gpt-5.4 gpt-4.1 \
  --reasoning-efforts none low medium high xhigh
```

This is the fastest way to debug a specific bad turn. It reuses the exact saved game prompt, runs it through the current client/player stack, records the requested and resolved reasoning settings, and checks whether the returned move is valid for the engine.

For direct OpenAI Responses API latency/setting probes outside the game engine, use:
```bash
docker-compose exec -T risk-game python /app/scripts/probe_openai_responses.py \
  --model gpt-5.5-pro \
  --prompt 'What is the capital of England? Reply with exactly one word.' \
  --efforts medium high \
  --verbosities medium high \
  --summaries omit auto
```

This is useful when you need to determine whether a model is slow on its own, whether a specific reasoning/verbosity/summary combination is the issue, or whether the slowdown only appears once the full Risk prompt stack is involved.

## Prompt Smoke Suite
Before starting a scored experiment batch, run the prompt smoke suite against the exact candidate models:
```bash
docker-compose exec -T risk-game python /app/scripts/run_prompt_smoke_suite.py \
  --agents \
    OpenAI:gpt-5.5 \
    OpenAI:gpt-5.4 \
    OpenAI:gpt-4.1 \
    Anthropic:claude-opus-4-7 \
    Gemini:gemini-3.1-pro-preview \
    Moonshot:kimi-k2.6
```

What it does:
- uses the real phase prompts from `PlayerAgent`
- runs a fixed board-state smoke scenario
- validates outputs with the real engine legality checks
- writes a JSON summary plus full prompt/response logs

Use this before long scored runs so prompt/parser issues are found before the experiment, not midway through it.

Current measured live-turn guidance from the smoke suite and follow-up setting probes:
- `claude-opus-4-7`: live-turn-safe in standard mode; adaptive thinking now also works after the client fix, but standard mode is the faster baseline.
- `gemini-3.1-pro-preview`: now has repeated clean smoke passes under the current timers; use it if you want the strongest currently visible Google candidate.
- `kimi-k2.6`: live-turn-safe only with thinking disabled. Thinking-enabled mode blows through the placement and turn budgets.

Reference artifacts:
- [Opus/Gemini/Kimi smoke pass](game_results/prompt_smoke_runs/game__2026-04-27_14-47-34/prompt_smoke_summary.md)
- [Gemini 3.1 repeat smoke pass](game_results/prompt_smoke_runs/game__2026-04-27_15-00-44/prompt_smoke_summary.md)
- [Opus + Kimi setting probe](game_results/model_probes/live_turn_setting_probes/game__2026-04-27_14-51-19/live_turn_setting_probe_results.json)
- [Opus thinking-enabled viability probe](game_results/model_probes/anthropic_thinking_viability/game__2026-04-27_14-59-34/anthropic_opus_47_thinking_probe.json)

## Experiment Batch Workflow
For long runs, use the experiment batch layer instead of ad hoc one-off commands. It is designed to minimize interactive monitoring and keep status in files.

The three main scripts are:
- `scripts/run_experiment.py`: starts a batch and writes manifest, status, results, and summary artifacts
- `scripts/experiment_status.py`: prints one compact status line or raw status JSON
- `scripts/experiment_summary.py`: recomputes and prints the final/partial experiment summary

Container examples:
```bash
docker-compose exec -T risk-game python /app/scripts/run_experiment.py \
  --label frontier_smoke \
  --preset live_turn_frontier \
  --num-games 3
```

Equivalent `make` wrapper:
```bash
make run-experiment ARGS="--label frontier_smoke --preset live_turn_frontier --num-games 3"
```

Status checks:
```bash
make experiment-status
make experiment-summary
```

The runner writes one experiment folder under `game_results/experiments/` with:
- `experiment_manifest.json`
- `experiment_status.json`
- `experiment_results.json`
- `experiment_summary.json`
- `experiment_summary.md`
- `preflight_results.json`
- one `game__...` folder per completed game

Current preset roster names:
- `openai_generation_ladder`
- `openai_size_ladder`
- `openai_mini_reasoning`
- `openai_mini_medium_vs_high`
- `openai_mini_high_strategic_hybrid`
- `openai_nano_reasoning`
- `live_turn_frontier`

Preset timing note:
- `openai_mini_reasoning` defaults to a more generous live budget of `120s` turn time and `25s` placement time unless you override those flags explicitly.
- `openai_mini_medium_vs_high` defaults to `300s` turn time and `50s` placement time, because it is intended specifically as a recovery test for `gpt-5.4-mini-high` against `gpt-5.4-mini-medium`.
- `openai_mini_high_strategic_hybrid` defaults to `300s` turn time and `25s` placement time, because it is intended to test `high` only on planning and attack while keeping placement, fortify, and card trade on `medium`.
- The preset varies reasoning across all game phases, including placement and card trade.
- Placement prompts are now much more compact and explicitly framed as fast local decisions, so the experiment still measures reasoning differences without wasting the budget on giant setup prompts.
- The default live-play prompt stack now matches the strongest probe architecture so far: `timed_risk_live` system prompt + compact execution prompts + attack-plan handoff. The heavier per-call `TIME BUDGET` and `FINAL CHECK` blocks are still available for probes, but they are no longer the default for scored play.
- All providers now use a shared Risk-specific system prompt profile by default: `timed_risk_live`. It frames the model as a timed competitive Risk agent, prioritizes legal timely actions, and tells the model to continue favorable attack chains instead of replanning the whole board after every small capture.

## Scenario Probes
For prompt and timing investigations, use the deterministic breakthrough probe instead of a full league. It keeps the real prompt/state/update loop but removes dice variance from the attack resolution.

```bash
docker-compose exec -T risk-game bash -lc 'cd /app && python scripts/probe_breakthrough_scenario.py --provider OpenAI --model gpt-5.4-mini --reasoning-effort high --variants minimal_baseline system_prompt_only system_plus_execution_handoff full_live --turn-time-limit-seconds 300 --placement-time-limit-seconds 25'
```

Supported variants / probe modes:
- `minimal_baseline`
- `system_prompt_only`
- `system_plus_execution_handoff`
- `full_live`
- `full`
- `no_time_budget`
- `no_final_check`
- `bare`

Mode meanings:
- `minimal_baseline`: old minimal system prompt, no time-budget block, no repeated final check, no attack-plan handoff.
- `system_prompt_only`: new `timed_risk_live` system prompt only, but still bare execution prompts.
- `system_plus_execution_handoff`: new system prompt plus the compact “planned next legal attack” handoff, but still bare execution prompts.
- `full_live`: new system prompt plus live-turn time budget, repeated final check, and attack-plan handoff.

Recommended low-token workflow:
1. Run `run_experiment.py` once and redirect stdout to a logfile if desired.
2. Check `experiment_status.py` only occasionally instead of rereading raw turn logs.
3. Use `experiment_summary.py` after completion for the digest.

## Running OpenAI Leagues
For repeated OpenAI-vs-OpenAI runs, use:
```bash
docker-compose exec -T risk-game python /app/scripts/run_openai_league.py \
  --label gpt54_family_league \
  --num-games 10 \
  --reasoning-effort medium \
  --placement-time-limit-seconds 15 \
  --turn-time-limit-seconds 90
```

This writes one saved game folder per game plus an aggregate summary JSON in `game_results/`.
Standard live-play timing policy in this repo:
- Initial placement and normal troop-placement prompts use a fast placement profile by default: `placement_reasoning_effort=low` and `placement_time_limit_seconds=15`.
- The opening setup remains the original alternating single-troop placement flow. It is not bulk-compressed into one move per player.
- Full turns use a hard `turn_time_limit_seconds=90` budget by default.
- If the turn timer expires, later strategic phases are skipped and the engine falls back quickly for any mandatory placement so the game continues.
- The engine keeps a small internal safety buffer inside the turn budget so observed wall-clock stays close to the configured limit in live runs.
- Long live runs now perform a cheap OpenAI preflight request before the league starts so quota/model-access failures are caught up front instead of halfway through a batch.

This is adjustable in experiment setup:
- in code via `GameConfig(turn_time_limit_seconds=...)`
- from the league runner via `--turn-time-limit-seconds ...`

Default live reasoning profile by phase:
- placement: `low`
- pre-turn planning: global requested effort capped at `medium`
- attack: global requested effort capped at `medium`
- fortify: global requested effort capped at `medium`
- card trade: global requested effort capped at `low`

The placement profile was benchmarked on the GPT-5.4 family and `low` was the best default that stayed safely inside the 15-second target across `gpt-5.4`, `gpt-5.4-mini`, and `gpt-5.4-nano`. Timed OpenAI calls use a hard worker-process timeout so the engine can actually forfeit a turn instead of waiting indefinitely on a stuck provider response. If an LLM call still fails, the engine records the raw provider error plus a fallback response in both the turn decision log and the per-call interaction log so the game can continue without hiding the cause.

## Contributing
Feel free to submit issues or pull requests.


## Roadmap
See [TODO.md](TODO.md) for the current prioritized development plan covering:
- engine hardening and regression tests
- game-state representation improvements for LLMs
- experiment framework refactors
- league and learning experiments
- reporting and analysis

For the durable project-history and research-memory view, also see [docs/development-log.md](docs/development-log.md).
For the current main experiment design, see [docs/experiment-program.md](docs/experiment-program.md).
