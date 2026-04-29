# Agent Instructions

This repository uses a container-first development workflow. If you are an automated coding agent or assistant, treat the Docker environment as the canonical runtime.

## Core Rule
- Do not install Python dependencies or run the project from the host machine unless the user explicitly asks for host-side work.
- Use the `risk-game` service defined in `docker-compose.yml`.
- Assume the application code is mounted into the container at `/app`.
- Assume `custom_startup.sh` will run `pip install -e /app` when the container starts.

## Standard Workflow
1. Start the dev environment:
   ```bash
   make up
   ```
   If `make` is unavailable:
   ```bash
   ./start_container.sh
   ```
2. Enter the application container:
   ```bash
   make shell
   ```
   Manual equivalent:
   ```bash
   docker exec -it risk-game-container bash
   ```
3. Run tests inside the container:
   ```bash
   make test
   ```
   This runs the deterministic regression suite only.
4. Run the example game inside the container:
   ```bash
   make run-example
   ```
5. Run live provider checks only when explicitly needed:
   ```bash
   make test-live
   ```
   For the cheapest real OpenAI paid-completion sanity check:
   ```bash
   make test-live-canary
   ```

## Repo-Specific Notes
- `docker-compose.yml` starts two services:
  - `risk-game`: the main Python development container
  - `qdrant`: the local vector store sidecar
- The project depends on `.env` for model/API credentials.
- The dev container image includes `make` and `sudo` by default.
- Prefer explicit provider model strings over numeric selectors when configuring experiments. The supported provider/model surface is documented in `docs/provider-models.md`.
- Python packages are intentionally installed inside the container, not in a host virtualenv.
- If you add tooling, scripts, or docs, prefer commands that execute through the container.

## Preferred Commands
```bash
make up
make shell
make test
make test-live
make test-live-canary
make run-example
make run-experiment ARGS="--label frontier_smoke --preset live_turn_frontier --num-games 3"
make experiment-status
make experiment-summary
make logs
make down
```

## Guardrails For Agents
- Keep README and container instructions in sync when changing the workflow.
- Prefer offline/deterministic tests for core game logic; keep live API tests separate.
- Treat `make test` as the required regression gate before changing engine logic.
- Do not introduce a host-only workflow as the default.
- If a command fails on the host because dependencies are missing, switch to the container workflow instead of installing ad hoc packages locally.
- Never print, commit, or rewrite `.env` secrets unless the user explicitly asks for credential work.

## Long-Running Game And Experiment Runs
- If the user asks you to run live games, experiments, leagues, or multi-game comparisons, let the full requested batch finish before closing out the task.
- Do not stop early just because a single game is slow, produces no intermediate output, or requires long model calls.
- Prefer `scripts/run_experiment.py` plus `scripts/experiment_status.py` / `scripts/experiment_summary.py` for long batches, or use the corresponding `make` wrappers.
- Prefer one long-running command or a background/log-to-file pattern over repeated short polling loops that can look like the run was stopped.
- If you need progress checks, make sure they do not terminate, restart, or duplicate the active run.
- If a turn or chat is interrupted while a live run may still be active, first check whether the underlying process is still running before launching a replacement run.
- When a run is intentionally capped for cost or time reasons, state that clearly before starting it. Do not silently shorten a requested experiment.
- For live experiment work, report results after the requested set of games completes, or report a hard failure if the run genuinely crashes or credentials/model access fail.
- When possible, inspect `experiment_status.json` or run `experiment_status.py` instead of tailing large raw logs repeatedly.

## Live Timing Policy
- Do not bulk-compress the initial setup flow. Opening placement remains alternating one troop at a time.
- Do not use `xhigh` reasoning for placement prompts.
- Default live placement profile: `placement_reasoning_effort=low` and `placement_time_limit_seconds=15`.
- Default live full-turn budget: `turn_time_limit_seconds=90`.
- Default live non-placement reasoning is phase-capped:
  - planning: cap at `medium`
  - attack: cap at `medium`
  - fortify: cap at `medium`
  - card trade: cap at `low`
- Keep a small internal safety buffer inside the configured turn budget so observed wall-clock lands near the real limit.
- If a turn deadline expires, let the engine forfeit the remaining strategic phases rather than waiting indefinitely on the model.
- For timed OpenAI calls, prefer the repo’s hard worker-process timeout path over softer client-only timeouts.
- Run the built-in OpenAI preflight check before long OpenAI leagues unless the user explicitly asks to skip it.
- When changing league or runner settings, keep `README.md` aligned with the actual enforced timing defaults.

## LLM Interaction Logs
- Live LLM prompt/response traffic should be written to `game_results/llm_interactions/<game_name>/...`.
- Keep the folder structure tracked in git, but do not commit runtime log files.
- These logs must preserve raw provider error text so quota, model-access, and API failures are diagnosable after the run.

## Related Files
- `README.md`: human-facing setup and usage
- `Makefile`: standard container commands
- `start_container.sh`: wrapper around `docker-compose up --build -d`
- `custom_startup.sh`: container startup hook
- `TODO.md`: development roadmap
