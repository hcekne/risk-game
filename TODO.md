# Risk Game Development TODO

## North Star
- [ ] Turn the repo into a reliable experiment platform for studying how different LLM agents play Risk, adapt between games, and differ strategically across providers and model variants.

Reference docs:
- [docs/experiment-program.md](docs/experiment-program.md): current planned hypothesis-driven experiment series
- [docs/development-log.md](docs/development-log.md): durable record of major engineering and research decisions
- [docs/experiment-suites/README.md](docs/experiment-suites/README.md): tracked archive of completed experiment analyses

## Current Status
- [x] Container-native deterministic regression suite exists and runs through `make test-regression`.
- [x] Core engine bugs found by regression tests have been fixed and locked with tests.
- [x] Multi-turn and multi-game scripted gameplay tests are in place.
- [x] Default live prompts now use the compact player-centric state view plus action-specific legal options.
- [x] Saved games now include turn-level strategic traces and a first-pass observable-strategy rubric.
- [x] Initial rubric calibration against a deterministic scripted sample has been documented.
- [x] Live experiment timing policy now enforces fast placement prompts (`low`, 15s) plus a 90s default full-turn budget without changing the alternating one-troop opening flow.
- [x] Timed OpenAI turns now use a hard worker-process timeout plus a small internal safety buffer so live turns actually forfeit near the configured limit.
- [x] Live prompt/response interaction logs and saved-prompt replay tools now exist for diagnosing provider/runtime issues.
- [x] Provider paid-completion canaries now exist for OpenAI, Gemini, and Moonshot, and Anthropic paid completion has been manually re-verified after key rotation.
- [x] `gpt-4.1` has been restored as a viable candidate after fixing invalid reasoning-effort overrides.
- [x] `gpt-5.5-pro` has been investigated and should currently be excluded from synchronous live-turn experiments.
- [x] Saved games now write a per-run `game_manifest.json` so later analysis does not depend on memory of the runtime settings.
- [x] A fixed prompt smoke suite now exists for pre-experiment validation of prompt/response compatibility across candidate models.
- [x] First live prompt-smoke passes have been run against the candidate roster, and the current live-turn-safe models are now clearer.
- [x] `claude-opus-4-7` has been restored as a viable Anthropic candidate after fixing the client path that broke its live calls.
- [x] `kimi-k2.6` has been verified as live-turn-viable only with thinking disabled.
- [x] `gemini-3.1-pro-preview` is now the locked Google candidate for the main experiment program.
- [x] A generic experiment batch runner plus compact status/summary scripts now exist for low-token long-run workflow.
- [ ] Representation benchmarking, experiment-runner refactoring, and between-game learning are still ahead.
- [ ] A clean non-LLM agent/engine path is still ahead.

## Recommended Build Order
1. Finish engine hardening with more scripted agent archetypes and cheap cross-provider smoke tests.
2. Lock the live-turn-safe model roster and rerun clean short baseline experiments.
3. Benchmark state representations and prompt packs on fixed board states.
4. Refactor experiments into configurable, reproducible runs.
5. Add a general non-LLM decision-policy path alongside LLM play.
6. Add between-game learning loops, budgets, and artifact tracking.
7. Run the main experiment matrix and write the follow-up report.

## 1. Validate Game Logic And Core Reliability
- [x] Expand offline test coverage for `GameState`, `Rules`, `GameMaster`, card trading, parsing, attack resolution, fortify validation, and victory conditions.
- [x] Add explicit game invariants after every turn:
  - Every territory has exactly one owner.
  - No territory has negative troops.
  - Eliminated players control zero territories.
  - Total territory count stays at 42.
- [x] Separate deterministic engine tests from live API/integration tests so CI can run without secrets.
- [x] Make the regression workflow container-native via `make test-regression`.
- [x] Add multi-turn and multi-game scripted gameplay regression tests that exercise the real `play_game()` loop.
- [x] Add a baseline scripted regression agent for deterministic engine coverage.
- [ ] Add a broader set of scripted agent archetypes for test diversity:
  - `RandomAgent`
  - `AggressiveAgent`
  - `TurtleAgent`
  - `ContinentAgent`
- [x] Add a cheap LLM smoke test mode for prompt/format validation only.
- [ ] Add an Anthropic paid canary test to match the OpenAI, Gemini, and Moonshot canaries.
- [ ] Add long-run soak tests that run 50-100 scripted games and summarize invariant failures.

## 2. Improve The LLM Game-State Representation And Prompts
- [x] Keep one canonical internal state and render LLM-facing views from it.
- [x] Add a compact player-centric default view for live play.
- [x] Add action-oriented summaries with legal placements, attack options, and fortify options.
- [x] Add derived features that reduce model reasoning load:
  - Continents controlled and continents close to completion
  - Border territories and threatened borders
  - Connected fortify options
  - Available attack edges with attacker/defender troop counts
  - Distance to territory-win target
- [x] Refactor the action prompts into a stable baseline prompt pack while preserving the existing parser/output grammar.
- [x] Add regression tests that lock prompt structure, legal-option summaries, and output grammar.
- [ ] Prototype a structured JSON/state block view for benchmarking only.
- [ ] Build a fixed benchmark set of board positions and questions to compare representations on:
  - State comprehension accuracy
  - Move legality
  - Strategic consistency
  - Output format compliance
  - Token cost and latency
- [ ] Benchmark alternative prompt packs:
  - Neutral baseline
  - More explicit legality-first prompts
  - Assisted/coached prompts for non-baseline experiments
- [ ] Decide whether the current compact view remains the permanent default after benchmarking.

## 3. Build The Experiment Framework
- [ ] Replace hard-coded agent mixes with a declarative experiment config:
  - Players
  - Model/provider
  - Prompt pack / knowledge system
  - State representation
  - Tool permissions
  - Ruleset
  - Number of games
  - Random seed policy
  - Learning enabled/disabled
  - Between-game time budget
- [ ] Add a model-viability registry or experiment note field so runs can explicitly encode:
  - live-turn safe
  - offline-analysis only
  - excluded due to latency
  - excluded due to output-format instability
- [ ] Store results in a consistent structure:
  - Per-turn state snapshots
  - Per-player metrics
  - End-game summary
  - Prompt/config snapshot
  - Learning artifacts created between games
- [x] Save a per-game manifest with the player roster, provider/model settings, and runtime rules/timers.
- [ ] Add experiment types:
  - `single_game_smoke`
  - `one_off_series_no_learning`
  - `provider_league_with_learning`
  - `model_lineage_comparison`
  - `representation_benchmark`
- [ ] Add aggregate reporting across runs:
  - Win rate
  - Placement by finish order
  - Survival length
  - Territory share over time
  - Card-trade efficiency
  - Attack success rate
  - Error rate / invalid move rate
  - Strategic rubric averages by player / model / prompt pack

## 4. Between-Game Learning System
- [ ] Define what agents are allowed to persist between games:
  - Notes / memory
  - Prompt refinements
  - Strategy docs
  - Small helper tools / engines
  - Opponent scouting reports
- [ ] Define hard constraints:
  - Fixed wall-clock budget per gap between games
  - Fixed compute/tool budget
  - Immutable archive of what changed after each game
- [ ] Decide whether agents learn privately, publicly, or with partial observability.
- [ ] Add a replay-analysis pipeline so agents can inspect previous games in a structured way rather than raw logs only.
- [ ] Add league-level anti-leakage rules so comparisons stay fair across providers and model variants.

## 5. Priority Experiments
- [ ] Experiment 0: Live-turn viability matrix
  - Short direct probes plus 1-game smoke runs
  - Goal: classify which models are usable in synchronous turn play before larger leagues
- [ ] Experiment A: Engine + representation smoke test
  - Scripted agents and cheap models
  - 10-20 short games
  - Goal: catch logic, parsing, and representation failures early
- [ ] Experiment B: One-off games with no learning
  - Same agent stack, repeated fresh games
  - Goal: measure baseline strategic strength
- [ ] Experiment C: Provider league with learning
  - 4 agents, 15 games, fixed time budget between games
  - Goal: measure adaptation and tool-building ability
- [ ] Experiment D: Model-lineage comparison
  - Variants from the same provider
  - Goal: isolate reasoning/model effects from tooling differences
- [ ] Experiment E: Representation ablation
  - Same base model, different state formats
  - Goal: quantify how much state representation changes play quality
- [ ] Experiment F: OpenAI live baseline after the runtime fixes
  - `gpt-5.5` vs `gpt-5.4` vs `gpt-4.1`
  - 3-5 games, no learning
  - Goal: establish a clean post-fix OpenAI baseline
- [ ] Experiment G: Cross-provider smoke league
  - Small number of games, strict inspection of timing and output compliance
  - Goal: verify provider/runtime compatibility before full leagues

## 6. Report Pipeline
- [ ] Define the core research questions before running the full league.
- [ ] Lock the metrics and plots before the main experiment run.
- [ ] Save enough metadata to reproduce every reported result.
- [x] Do an initial manual calibration pass for the observable-strategy rubric.
- [ ] Do a second calibration pass on live LLM games before treating the rubric as a headline metric.
- [ ] Draft the follow-up report in parallel with experiments:
  - Setup
  - Rules and constraints
  - Agent architectures
  - Representation choices
  - Main results
  - Notable failures and strategies
  - Limits and threats to validity

## 7. Non-LLM Engine Track
- [ ] Define a clean decision-policy abstraction so `GameMaster` is not conceptually tied only to LLM prompt agents.
- [ ] Decide the first integration path for non-LLM players:
  - local client compatible with the existing `PlayerAgent` parser contract
  - dedicated non-LLM agent class with structured actions
  - shared policy interface implemented by both
- [ ] Promote heuristic/scripted agents from test helpers into first-class experiment agents.
- [ ] Build a first heuristic engine baseline that reasons over structured game state directly.
- [ ] Add self-play support for non-LLM agents so the repo can be used as a training/evaluation arena.
- [ ] Evaluate whether the cleanest long-term architecture is:
  - in-process Python policy execution
  - local API/server inside the container
  - external engine process with a narrow adapter
- [ ] Keep the same turn summaries, metrics, and experiment artifacts for both LLM and non-LLM agents so comparisons remain apples-to-apples.

## Immediate Next Steps
- [x] Finish engine-level regression coverage and make it runnable without live APIs.
- [x] Improve the default live state view and baseline prompts without breaking the parser.
- [ ] Add `RandomAgent`, `AggressiveAgent`, `TurtleAgent`, and `ContinentAgent`.
- [ ] Add a cheap provider smoke suite that checks prompt understanding, latency, and output-format compliance across OpenAI, Anthropic, and Gemini.
- [x] Add a cheap provider smoke suite that checks prompt understanding, latency, and output-format compliance across OpenAI, Anthropic, Gemini, and Moonshot.
- [x] Run the prompt smoke suite on the initial candidate roster before starting the first scored batch.
- [ ] Re-run a clean short OpenAI baseline with `gpt-5.5`, `gpt-5.4`, and `gpt-4.1`.
- [x] Decide and document the current live-turn-safe model roster in the experiment docs.
- [ ] Design and benchmark 2-3 candidate state representations on fixed board states.
- [ ] Refactor experiment setup into a config-driven runner before building the league mode.
- [ ] Add the first non-LLM policy abstraction/design pass before between-game learning work expands the architecture further.
- [ ] Only then implement the between-game learning workflow.
