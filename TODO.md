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
- [x] A balanced salvaged `16`-game strategic provider result now exists and currently favors `gemini-3.1-pro-preview`.
- [x] A second clean `16`-game provider replicate now exists and reproduces the Gemini lead.
- [x] A generic experiment batch runner plus compact status/summary scripts now exist for low-token long-run workflow.
- [x] Provider quota/billing pause-resume handling now exists for preflight and live prompt calls, with regression coverage.
- [x] A pooled `32`-game provider result now exists and currently supports Gemini as the strongest tested provider representative under the frozen strategic live-turn condition.
- [ ] Representation benchmarking, experiment-runner refactoring, and between-game learning are still ahead.
- [ ] A clean non-LLM agent/engine path is still ahead.

## Recommended Build Order
1. Finish engine hardening with more scripted agent archetypes and cheap cross-provider smoke tests.
2. Run Kimi capability anchoring against historical OpenAI, Gemini, and Anthropic anchors, preferably as separate duplicate-team `2x2` arenas that can be launched in parallel.
3. Benchmark state representations and prompt packs on fixed board states.
4. Refactor experiments into configurable, reproducible runs.
5. Add a general non-LLM decision-policy path alongside LLM play.
6. Add between-game learning loops, budgets, and artifact tracking.
7. Extend the provider program only if a new provider release or a cost-efficiency result reopens the winner question.

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
- [x] Add provider-failure handling and operator pause/resume flow for live runs:
  - Detect provider billing/quota/auth/rate-limit failures from raw provider error text without masking the original message.
  - Surface a high-signal run-level alert in console output and persisted experiment status when repeated provider failures indicate the run is no longer clean.
  - Pause the active run instead of failing or silently burning credits with other providers when an out-of-credit or similar provider-account error is detected.
  - Wait for explicit operator feedback before resuming, with a simple terminal input path suitable for `tmux` / SSH sessions.
  - On resume, retry the blocked step cleanly instead of skipping phases or advancing the game in a degraded fallback state.
  - Record pause/resume timestamps and the triggering provider/error in experiment artifacts so contaminated runs are easy to audit later.
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
  - Input/output token totals by player / provider / model
  - Estimated API cost totals and cost-per-win style ratios

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
- [x] Experiment F: Confirmatory cross-provider strategic replicate
  - current roster: Gemini vs Claude vs OpenAI (`gpt-5.1` exec + `gpt-5.5` plan) vs Kimi
  - `16` games, same strategic `90 / 90 / 15` condition
  - Outcome: Gemini replicated the `10 / 16` win result and remains the current provider leader under the frozen strategic condition
- [ ] Experiment G: Cross-provider smoke league
  - Small number of games, strict inspection of timing and output compliance
  - Goal: verify provider/runtime compatibility before full leagues
- [x] Experiment H: Kimi capability anchoring vs OpenAI
  - first pass: `2x kimi-k2.6` vs `2x gpt-4.1`
  - `16` games under the strategic `90 / 90 / 15` condition
  - Outcome: duplicated `gpt-4.1` beat duplicated `kimi-k2.6` `9-7`, but the gap was fully compatible with chance and Kimi was materially cheaper
- [x] Experiment I: Kimi capability anchoring vs Gemini
  - first pass: `2x kimi-k2.6` vs `2x gemini-2.5-pro`
  - `16` games under the strategic `90 / 90 / 15` condition
  - Outcome: duplicated `gemini-2.5-pro` beat duplicated `kimi-k2.6` `9-7`; Kimi remains cost-efficient, but the current evidence places it somewhat below the Gemini 2.5 Pro tier in this environment
- [x] Experiment J: Kimi capability anchoring vs Anthropic
  - first pass: `2x kimi-k2.6` vs `2x claude-sonnet-4-20250514`
  - `16` games under the strategic `90 / 90 / 15` condition
  - Outcome: duplicated `kimi-k2.6` beat duplicated `claude-sonnet-4-20250514` `9-7`; the win gap was not decisive, but Kimi was far cheaper and much less timeout-prone
- [x] Anthropic Sonnet 4.5 follow-up archived
  - `2x kimi-k2.6` vs `2x claude-sonnet-4-5-20250929`
  - completed, but not part of the main story
  - Reason: severe runtime mismatch under the current harness and missing pricing support for `claude-sonnet-4-5-20250929`
- [ ] Experiment K: Gemini execution planner bakeoff
  - lineup: `gemini-3.1-full` vs `gpt-5.5-plan_gemini-3.1-exec` vs `claude-opus-4-7-plan_gemini-3.1-exec` vs `kimi-k2.6-plan_gemini-3.1-exec`
  - first pass: `16` games under the strategic `90 / 90 / 15` condition
  - follow-up replicate pool: four parallel `8`-game shards (`rep2a` / `rep2b` / `rep2c` / `rep2d`) using the same frozen roster, for a pooled `48`-game total once combined with the original `16`
  - Goal: isolate planning quality while holding the operational execution layer fixed at the current strongest executor
- [x] Experiment L: Gemini 3 Flash execution cost gate
  - lineup: `gemini-3.1-pro-full` vs `gemini-3-flash-full` vs `gemini-3.1-plan_gemini-3-flash-exec`
  - first pass: `15` games under the strategic `90 / 90 / 15` condition
  - parallel shard option: five `3`-game shards with labels `gemini3_flash_execution_cost_gate_shard_[a-e]_3`; pool the five clean shards into one `15`-game series artifact after completion
  - Outcome: pooled `15` games support `gemini-3.1-plan_gemini-3-flash-exec` as the practical default scaffold; pure Flash is viable but weaker, and Pro-full is much more expensive
  - Goal: test whether `gemini-3-flash-preview` is cheap enough and strong enough to replace `gemini-3.1-pro-preview` as the default execution layer before running further planner-only bakeoffs
- [ ] Experiment M: Cost-optimized hybrid planner championship
  - precondition: finish Experiment L and lock the cheapest Gemini execution scaffold that preserves most of the `gemini-3.1-pro-preview` baseline strength
  - locked scaffold after Experiment L: `gemini-3.1-pro-preview` planning + `gemini-3-flash-preview` execution is now the current practical default until contradicted by a larger rerun
  - lineup: `gemini-3.1-plan_gemini-3-flash-exec` vs `gpt-5.5-plan_gemini-3-flash-exec` vs `claude-opus-4-7-plan_gemini-3-flash-exec` vs `kimi-k2.6-plan_gemini-3-flash-exec`
  - first pass: `16` games under the strategic `90 / 90 / 15` condition
  - parallel shard option: four `4`-game shards with labels `gemini3_flash_execution_planner_hybrid_bakeoff_shard_[a-d]_4`; pool the four clean shards into one `16`-game series artifact after completion
  - replicate option: four more `4`-game shards with labels `gemini3_flash_execution_planner_hybrid_bakeoff_rep2_shard_[a-d]_4`; pool both `16`-game blocks into a `32`-game series if the first pass stays inconclusive
  - Outcome after pooled `32`: no planner winner is established on wins; execution standardization appears to compress most of the provider spread into a roughly equal planning band
  - Goal: compare planning quality after execution cost has been driven down to a practically deployable Gemini scaffold
- [ ] Experiment M2: Direct Claude-vs-Kimi planner duel on Flash execution
  - rationale: the pooled `32`-game four-way planner bakeoff suggests only a weak Claude-over-Kimi edge, but the 4-way field is too sample-inefficient to resolve it cleanly
  - lineup: `2x claude-opus-4-7-plan_gemini-3-flash-exec` vs `2x kimi-k2.6-plan_gemini-3-flash-exec`
  - first pass: `16` games via four `4`-game shards
  - Outcome: pooled `16` finished `9-7` for Claude, but the result remained fully compatible with chance; Claude is descriptively cleaner, but the primary-endpoint gap is still too small for a strong claim
  - Takeaway: further planner-only head-to-head grinding is probably lower ROI than either mechanistic trace analysis or a cheaper fixed-board benchmark
  - lineup: `2x claude-opus-4-7-plan_gemini-3-flash-exec` vs `2x kimi-k2.6-plan_gemini-3-flash-exec`
  - first pass: `16` games as four `4`-game shards
  - shard labels: `claude_vs_kimi_flash_exec_planner_team_shard_[a-d]_4`
  - Goal: convert the soft four-way planner signal into a direct, higher-power Claude-vs-Kimi estimate under the same cheap execution scaffold
- [ ] Experiment N: Cheap benchmark-agent lock
  - precondition: finish Experiment M
  - Goal: freeze one strong but reasonably cheap Gemini-based benchmark agent for later evaluation of non-LLM or rules-based Risk engines
  - downstream use: repeated evaluation opponent for future engine/harness work without paying full frontier-model costs on every run

## 6. Report Pipeline
- [ ] Define the core research questions before running the full league.
- [ ] Lock the metrics and plots before the main experiment run.
- [ ] Save enough metadata to reproduce every reported result.
- [x] Do an initial manual calibration pass for the observable-strategy rubric.
- [ ] Do a second calibration pass on live LLM games before treating the rubric as a headline metric.
- [ ] Frame the final write-up around both model capability and system design:
  - Which models are strongest full-stack live agents?
  - Which models are strongest planners once execution is fixed?
  - How much can cost be reduced by decomposing the agent into planning and execution layers?
  - What does this imply for real-world LLM system design beyond Risk itself?
- [ ] Draft the follow-up report in parallel with experiments:
  - Setup
  - Rules and constraints
  - Agent architectures
  - Representation choices
  - Main results
- [x] Add a planning-trace analysis pass for goal-directedness / agentic drive using the saved observable planning outputs rather than hidden reasoning:
  - detect explicit target tracking such as “need X more territories,” “reach 65%,” “break bonus to stay on path,” or “advance the fastest path to target”
  - compare how often models re-anchor on the game objective after setbacks or blocked attack lines
  - separate simple keyword counting from a smaller manual coding pass so the write-up can distinguish raw language frequency from genuinely goal-directed planning structure
  - test whether Gemini’s observed win edge is partly explained by more persistent objective tracking in the planning text
  - Outcome: the pooled provider `32` trace analysis now shows a large Gemini edge in explicit win-target tracking and quantified objective language
  - Notable failures and strategies
  - Limits and threats to validity
- [x] Add a provider-32 execution-trace analysis pass to explain what converts Gemini's provider lead into wins:
  - inspect saved `turn_summary_turn_*.json` traces and `llm_decisions`
  - compare attack-chain depth, zero-attack turns, midgame territory conversion, and phase-level fallback / invalid rates
  - Outcome: Gemini's edge appears to come from deep conquest-chain conversion rather than from being the single cleanest runtime
- [x] Package the paper arc before drafting:
  - define the central thesis
  - map claims to evidence
  - structure the source article so both humans and AIs can parse it easily
  - Outcome: a tracked arXiv-style storyline arc now exists in `docs/article-plans/`
- [ ] Prepare audience-specific output set after the main analysis is stable:
  - research-style longform article as the source document
  - `~1500` word LinkedIn newsletter version focused on practical lessons for builders
  - a narrower Towards Data Science article focused on experimental design, evaluation, and system decomposition
  - `3` shorter LinkedIn posts built from the strongest individual findings
  - a YouTube manuscript built around the “how to choose and compose LLMs for an agent system” angle

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
- [x] Add quota/billing-aware pause handling for live experiments so out-of-credit runs stop and wait for operator input instead of burning more provider credits or ending in contaminated fallback-heavy batches.
- [ ] Trim live console noise after the current validation pass so the game is easier to follow from the terminal while keeping the phase-completion timing lines, saved-plan summaries, and high-signal attack summaries.
- [ ] Run a clean confirmatory replicate of the current cross-provider strategic lineup now that pause/resume handling is in place.
- [ ] Prepare the first Kimi anchoring ladder against OpenAI once the confirmatory provider replicate is complete.
- [ ] Prepare follow-on Kimi anchoring ladders against Gemini and Anthropic if the first anchor run still leaves the capability tier ambiguous.
- [x] Decide and document the current live-turn-safe model roster in the experiment docs.
- [ ] Design and benchmark 2-3 candidate state representations on fixed board states.
- [ ] Refactor experiment setup into a config-driven runner before building the league mode.
- [ ] Add the first non-LLM policy abstraction/design pass before between-game learning work expands the architecture further.
- [ ] Only then implement the between-game learning workflow.
