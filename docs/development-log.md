# Development Log

This file is the persistent project memory for important engineering and research decisions.

It serves two purposes:
- keep future development grounded in what has already been learned
- preserve evidence and rationale that can later be used in the follow-up article about LLM strategic play in Risk

## Working Principles

- Treat the repo as an experiment platform first, and a game demo second.
- Prefer deterministic regression coverage before adding new live experiment complexity.
- Keep live-provider failures diagnosable by saving prompts, raw responses, timing, and provider errors.
- Evaluate strategic behavior from observable artifacts, not hidden chain-of-thought.
- Separate `model is bad at the task` from `the runtime/prompt/config is broken`.

## Current Research Priority

- The confirmatory provider replicate is now complete, and the pooled `32`-game provider result currently supports `gemini-3.1-pro-preview` as the strongest tested provider representative under the frozen strategic live-turn condition.
- The next article-grade question is not another provider roster search but a capability-anchoring study for `kimi-k2.6`.
- That anchoring study should be framed as a provider-anchor comparison, not a literal "months behind" claim, unless the accessible historical model grid is dense enough to justify a time-based translation.
- The first-pass Kimi anchoring design should use duplicate-team `2x2` arenas against one anchor family at a time so family-level strength can be estimated with lower variance and parallelized execution.
- The broader narrative is now shifting from pure model ranking to **LLM system design**:
  - which model should plan?
  - which model should execute?
  - where can cost be cut without giving away too much strength?
  - how do we build a benchmark agent strong enough to test future non-LLM engines?

### Cost estimation is now a tracked research dimension

The experiment summaries now estimate API cost from saved usage metadata and a local pricing snapshot rather than from manual billing inspection.

Current rule:
- cost claims should cite the local pricing snapshot and stay explicitly labeled as estimates
- historical runs before usage logging landed should not be used for cost-per-win comparisons
- cost metrics are now first-class secondary outcomes because they materially affect real-world deployability for live agent systems

### 2026-05-09 next-stage roadmap shifts from provider ranking to cheap benchmark-agent construction

The provider winner question is now materially clearer than it was at the start of the project:
- Gemini is the current full-stack leader under the frozen live strategic condition
- Kimi has now been triangulated against older OpenAI, Gemini, and Anthropic anchor tiers

That means the next stage should optimize for practical benchmark construction, not more provider leaderboard churn.

The staged plan is:
- first, finish the `gemini-3-flash-preview` execution cost gate
- second, if Flash preserves enough strength, use that cheaper Gemini scaffold as the execution layer in a planner-only hybrid championship
- third, freeze the winning cheap Gemini-based hybrid as the benchmark agent for later non-LLM engine work

This matters because future engine or rules-based systems will need a strong but affordable LLM baseline opponent. A full frontier-model stack is too expensive for large-scale repeated evaluation.

### 2026-05-09 goal-directed planning language is now an explicit analysis target

There is now a working hypothesis that part of Gemini's live-game edge comes from more persistent goal direction in its observable planning text.

The specific claim to test is not “Gemini sounds smarter.” It is narrower:
- Gemini may track the game objective more explicitly
- Gemini may more often quantify distance to the `65%` win target
- Gemini may re-anchor on the win condition more consistently after setbacks or blocked lines
- that style of planning may help in bounded agent loops where objective drift is costly

Methodological constraint:
- study only the saved observable planning outputs already written to the interaction logs
- do not rely on hidden reasoning or unavailable chain-of-thought
- combine simple lexical/phrase counts with a smaller manual coding pass so the later write-up can distinguish surface wording from genuinely goal-directed planning structure

### 2026-05-09 Gemini 3 Flash cost gate picks a cheap scaffold without collapsing strength

Saved pooled series:
- `/shared-game-results/experiment_series/gemini3_flash_execution_cost_gate_15_pooled`

Headline result:
- `gemini-3.1-plan_gemini-3-flash-exec` won `8 / 15`
- `gemini-3.1-pro-full` won `4 / 15`
- `gemini-3-flash-full` won `3 / 15`

Interpretation:
- pure Flash execution is viable
- pure Flash planning gives away enough that it should not be the default benchmark scaffold
- `gemini-3.1-pro-preview` planning on `gemini-3-flash-preview` execution is far cheaper than `gemini-3.1-pro-preview` full-stack while performing better on the primary endpoint in this pooled cost-gate batch

Operational decision:
- lock `gemini-3.1-pro-preview` planning + `gemini-3-flash-preview` execution as the current practical scaffold for the next planner-only hybrid championship

This is a practical system-design decision, not yet a publication-grade theorem that the hybrid dominates all Gemini variants. The point of the cost gate was to choose a strong and affordable execution layer for the next stage, and it succeeded.

### 2026-05-09 pooled 32-game Flash-exec planner bakeoff is mostly a near-equality result

Saved pooled series:
- `/shared-game-results/experiment_series/gemini3_flash_execution_planner_hybrid_bakeoff_32_pooled`

Headline result:
- Claude planner: `10`
- Gemini planner: `8`
- GPT-5.5 planner: `8`
- Kimi planner: `6`

Interpretation:
- once execution is standardized to `gemini-3-flash-preview`, the remaining planning differences are much smaller than the earlier full-stack provider gaps
- the pooled winner split is fully compatible with near-equality on wins
- the more important result is therefore structural, not leaderboard-based: decomposition removed much of the provider spread

Practical consequence:
- do not overclaim a planner winner from this pooled `32`
- if the next question is specifically Claude vs Kimi planning quality, switch from the four-way bakeoff to a direct duplicate-team `2x2` duel on the same Flash execution scaffold

### 2026-05-10 direct Claude-vs-Kimi Flash-exec duel still does not separate the planners

Saved pooled series:
- `/shared-game-results/experiment_series/claude_vs_kimi_flash_exec_planner_team_16_pooled`

Headline result:
- Claude team: `9`
- Kimi team: `7`

Interpretation:
- the direct duel removes the sample-efficiency problem from the earlier four-way planner bakeoff
- even so, the outcome remains a near-parity result on wins
- Claude looks cleaner on secondary metrics:
  - faster
  - lower fallback burden
  - higher strategic score
- Kimi remains competitive enough on the primary endpoint that a strong `Claude > Kimi` planning claim is still not justified

The broader lesson is unchanged:
- once execution is standardized to a strong cheap Gemini scaffold, the remaining planner differences are much smaller than the earlier full-stack provider gaps
- more brute-force planner duels have sharply diminishing returns unless they are tied to a much more focused mechanistic question

### 2026-05-10 provider-32 trace analyses now support a mechanism story

Saved trace-analysis artifacts:
- `/shared-game-results/experiment_series/frontier_strategic_provider_32_pooled/trace_analysis/planning_trace_metrics.json`
- `/shared-game-results/experiment_series/frontier_strategic_provider_32_pooled/trace_analysis/execution_trace_metrics.json`

Tracked notes:
- [2026-05-10_provider32-goal-directedness-trace-analysis.md](experiment-suites/2026-q2-strategic-tests/2026-05-10_provider32-goal-directedness-trace-analysis.md)
- [2026-05-10_provider32-execution-trace-analysis.md](experiment-suites/2026-q2-strategic-tests/2026-05-10_provider32-execution-trace-analysis.md)

Headline findings:
- Gemini is the only provider in the pooled `32`-game provider series that tracks the win objective explicitly in a large share of its visible plans
- that explicit goal tracking rises sharply as Gemini approaches the `65%` win target
- on execution, Gemini is not the cleanest runtime, but it converts more turns into deep conquest chains than the rest of the field
- Claude is cleaner, GPT is heavily timeout-dragged, and Kimi is less continuous in attack/fortify execution

Interpretation:
- the project now has both outcome-level evidence and mechanism-level evidence
- that is enough to move the eventual write-up from a leaderboard report toward a live-agent systems paper

### 2026-05-10 paper planning is now explicit

Saved paper-arc document:
- [2026-05-10_live-agent-risk-arxiv-arc.md](article-plans/2026-05-10_live-agent-risk-arxiv-arc.md)

Working framing:
- this should be written as a live-agent systems study under bounded strategic execution
- not as a universal intelligence ranking

### 2026-05-09 dissemination should translate the experiments into a broader system-design lesson

The eventual output should not stop at “Gemini won this tournament” or “Kimi is roughly at this older tier.”

The stronger public lesson is:
- model benchmarking inside a real agent loop exposes weaknesses that leaderboard-style evaluations hide
- the best end-to-end system may be a hybrid, not a single flagship model
- task decomposition across planning and execution can improve both cost and performance
- real builders should evaluate models as components of workflows, not just as standalone chatbots

Planned output stack:
- one research-style source article
- one `~1500` word LinkedIn newsletter post
- one narrower Towards Data Science piece
- three short LinkedIn posts
- one YouTube manuscript

These should all share the same evidence base but emphasize different takeaways for different audiences.

### 2026-05-07 provider replication confirms the Gemini lead

The provider winner question is now materially clearer than it was after the first balanced `16`.

Saved results:
- balanced salvaged provider series: `/shared-game-results/experiment_series/frontier_strategic_full_16_salvaged`
- clean direct provider replicate: `/shared-game-results/experiments/experiment__2026-05-06_11-13-05__frontier_strategic_replicate_2_16`
- pooled provider series: `/shared-game-results/experiment_series/frontier_strategic_provider_32_pooled`

Headline result:
- Gemini won `10 / 16` in the balanced salvaged block
- Gemini won `10 / 16` again in the clean direct replicate
- pooled over `32` games, Gemini now has `20` wins against GPT-5.1 `6`, Claude `4`, and Kimi `2`

Interpretation:
- the identity of the provider winner is now stable enough to treat Gemini as the current best model in this tested field and deployment condition
- the unresolved secondary question is GPT-5.1 versus Claude for second place, not who wins overall
- future provider-wide reruns should be justified by a changed roster, pricing/cost question, or methodology shift rather than by residual doubt about the Gemini lead itself

### 2026-05-08 Kimi vs GPT-4.1 anchor suggests near-parity with a strong cost advantage

Saved experiment:
- `/shared-game-results/experiments/experiment__2026-05-07_15-34-43__kimi_anchor_openai_gpt41_team_16`

Headline result:
- duplicated `gpt-4.1` team beat duplicated `kimi-k2.6` team `9-7`
- that win gap is fully compatible with chance on an exact binomial read

Interpretation:
- Kimi does not look like a current-provider-frontier model in this environment
- but it does look broadly competitive with the `gpt-4.1` anchor tier
- Kimi is also materially cheaper on the new cost instrumentation, which makes the anchor result more practically important than a simple win table would suggest

### 2026-05-08 Kimi vs Gemini 2.5 Pro anchor puts Kimi below an older Google tier

Saved experiment:
- `/shared-game-results/experiments/experiment__2026-05-07_15-35-19__kimi_anchor_gemini25pro_team_16`

Headline result:
- duplicated `gemini-2.5-pro` team beat duplicated `kimi-k2.6` team `9-7`
- the result is directional rather than overwhelming:
  - one-sided exact binomial `p ≈ 0.038`
  - two-sided exact binomial `p ≈ 0.077`

Interpretation:
- Kimi looks somewhat weaker than the Gemini 2.5 Pro anchor tier in this environment
- the gap is real enough to take seriously, but still smaller than a casual “frontier versus weak open model” narrative would suggest
- Kimi remains materially better on cost efficiency, even while losing the strength comparison

Most useful public framing:
- Google announced Gemini 2.5 Pro on `2025-03-25`, with GA on `2025-06-17`
- Moonshot announced Kimi K2.6 on `2026-04-21`
- so Kimi 2.6 arrives roughly `10-13` months after Gemini 2.5 Pro depending on which Gemini milestone is used
- yet in this live strategic setting Kimi only reaches near-parity / modestly trails that older Gemini tier

That is not a literal “months behind” theorem, but it is a strong and defensible interpretation of the current anchor evidence.

### 2026-05-08 Kimi vs Anthropic Sonnet 4 (20250514) shows operational parity or better

Saved experiment:
- `/shared-game-results/experiments/experiment__2026-05-07_17-43-42__kimi_anchor_anthropic_sonnet4_20250514_team_16`

Headline result:
- duplicated `kimi-k2.6` team beat duplicated `claude-sonnet-4-20250514` team `9-7`
- that win gap is fully compatible with chance on an exact binomial read

Interpretation:
- Kimi does not look clearly stronger than this older Anthropic Sonnet tier
- but it does look fully competitive, and descriptively ahead, on the primary endpoint
- more importantly, Kimi reaches the actual `65%` victory condition more often, while the Sonnet team wins more often by surviving to the round cap

Operationally, the difference is sharper than the win table:
- Sonnet posts higher rubric scores, but it times out constantly under this harness
- Kimi is much cheaper and far less timeout-prone
- so in live deployment terms, Kimi is arguably the better agent here even without a decisive statistical win gap

This sharpens the current anchor picture:
- near GPT-4.1
- below Gemini 2.5 Pro
- competitive with this older Anthropic Sonnet tier
- still clearly below the current Gemini 3.1 frontier result

### 2026-05-08 Anthropic Sonnet 4.5 follow-up should be archived from the main story

Saved experiment:
- `/shared-game-results/experiments/experiment__2026-05-07_17-43-31__kimi_anchor_anthropic_sonnet45_team_16`

Why it is not a good anchor candidate:
- Sonnet 4.5 under the current thinking-enabled full-stack live harness is an extreme runtime mismatch
- each Claude copy averaged roughly `24.5-25.5` fallback calls and roughly `10.6-10.8` timed-out turns per game
- the pricing table is missing `claude-sonnet-4-5-20250929`, so the cost side of the run is incomplete

Interpretation:
- the run is more a demonstration of deployment mismatch than of clean capability anchoring
- it does not add much beyond the older Sonnet 4 anchor that already places Kimi around parity with an older Anthropic tier

Decision:
- archive Sonnet 4.5 from the main anchoring narrative
- keep Sonnet 4 (20250514) as the Anthropic anchor for this story

## Key Decisions And Findings

### Container-first runtime is the standard

- The canonical development workflow is inside the Docker environment, not the host Python environment.
- Live tests, regression tests, and experiment runs should be executed in-container so environment drift does not contaminate results.

Related docs:
- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)

### Deterministic engine testing comes before large live runs

- The repo now has container-native regression coverage for engine logic, invariants, parsing, capitals mode, turn flow, and multi-game scripted gameplay.
- Scripted gameplay tests are required because unit tests alone do not prove the engine survives real turn loops.

Why this matters:
- Large league runs are too expensive and too slow to use as the first line of bug discovery.
- Engine regressions must be caught offline before live model comparisons mean anything.

### State representation and prompts were simplified to reduce model workload

- The default LLM view is now a compact player-centric board summary instead of a verbose territory dump.
- Action prompts now put legality and exact output format ahead of any strategic framing.
- Legal placement, attack, and fortify options are precomputed so models do less rule reconstruction.

Why this matters:
- We want better strategic play from the models, not more token spend on reconstructing game mechanics.
- This also makes cross-model comparisons fairer because the engine, not the model, does more of the legality bookkeeping.

### Observable strategy is now a first-class artifact

- Saved games include turn summaries, action reasons, plan summaries, and a first-pass strategy rubric.
- The project explicitly measures observable strategic traces rather than hidden provider reasoning.

Why this matters:
- This keeps analysis reproducible and comparable across providers.
- It also gives the article a more defensible methodology.

Related docs:
- [strategic-analysis.md](strategic-analysis.md)
- [strategic-rubric-calibration.md](strategic-rubric-calibration.md)

### Live experiments need explicit timing policy

- Default live turn budget: `90s`
- Default placement budget: `15s`
- Opening setup remains alternating one troop at a time
- If a turn budget is exhausted, mandatory placement falls back and later strategic phases are forfeited

Why this matters:
- Without hard timing limits, some models can stall live games for hours.
- Human online Risk commonly uses a bounded turn timer, so this is a fairer and more realistic constraint anyway.

### Provider canaries are required before long paid runs

- A metadata check is not enough to prove a provider key is usable.
- The repo now treats a real paid completion as the correct liveness check.
- OpenAI canary: `make test-live-canary`
- Anthropic was also manually verified with a direct live completion during setup work on April 27, 2026.

Why this matters:
- Earlier runs were polluted by quota and key issues that were not caught soon enough.
- Long leagues should not start unless the paid completion path is verified first.

### `gpt-4.1` was initially misclassified as weak, but the real issue was config incompatibility

What happened:
- In the first four-way OpenAI run, `gpt-4.1` repeatedly failed placement and looked strategically poor.

What we later found:
- The runtime was incorrectly passing `reasoning_effort` overrides to `gpt-4.1`, which does not support them.
- Those failures happened locally before meaningful model completions.

Evidence:
- Saved failure trace: [gpt-4.1 placement log](../game_results/llm_interactions/game__2026-04-26_21-05-36/gpt-4.1/round_00/initial_setup/0001_initial_troop_placement.json)
- Live replay after the fix: [gpt41_initial_probe_2026-04-27.json](../game_results/model_probes/gpt41_initial_probe_2026-04-27.json)

Decision:
- Do not treat the original poor `gpt-4.1` game result as a clean strategic signal.
- `gpt-4.1` remains a viable live-turn candidate.

### `gpt-5.5-pro` is not suitable for synchronous live-turn Risk play

This is the most important current model-selection conclusion.

What we found:
- `gpt-5.5-pro` supports only `reasoning.effort` values `medium`, `high`, and `xhigh`.
- It does not support the low-latency placement profile that works for the GPT-5.4 family.
- Even when the invalid-placement-config bug was fixed, `gpt-5.5-pro` remained too slow or too reasoning-heavy for live Risk turns.

Direct probe findings:
- On a trivial direct prompt, `What is the capital of England?`, it did complete successfully, but with noticeable and variable latency.
- Repeated direct runs landed roughly in the `3.5s` to `12.4s` range for very small prompts.
- On an actual saved Risk placement prompt, it consumed the full token budget as reasoning tokens and emitted no move text:
  - at `128` max output tokens: no move text
  - at `512` max output tokens: still no move text

Evidence:
- Simple direct matrix: [gpt55pro_capital_matrix_64tok_2026-04-27.json](../game_results/model_probes/gpt55pro_capital_matrix_64tok_2026-04-27.json)
- Repeated simple direct runs: [gpt55pro_capital_repeats_2026-04-27.json](../game_results/model_probes/gpt55pro_capital_repeats_2026-04-27.json)
- Direct saved-placement probe: [gpt55pro_saved_placement_direct_2026-04-27.json](../game_results/model_probes/gpt55pro_saved_placement_direct_2026-04-27.json)

Interpretation:
- `gpt-5.5-pro` is not broken in the sense of "cannot answer anything".
- It is broken for this use case because synchronous turn-based play needs bounded latency and guaranteed visible action output.
- A model that spends the entire output budget on reasoning tokens without emitting a move is operationally unusable for this engine.

Decision:
- Exclude `gpt-5.5-pro` from live turn-by-turn Risk leagues.
- Reserve it for offline or asynchronous work:
  - post-game analysis
  - strategy synthesis between games
  - report drafting
  - experiment interpretation

This decision should be retained unless a future API/runtime mode changes the observed behavior materially.

### `gpt-5.5`, `gpt-5.4`, and likely `gpt-4.1` are the current OpenAI live-turn candidates

Current working roster for synchronous OpenAI live play:
- `gpt-5.5`
- `gpt-5.4`
- `gpt-4.1`
- `gpt-5.4-mini`
- `gpt-5.4-nano`

Current exclusion from live turn play:
- `gpt-5.5-pro`

This is a practical experiment-policy decision, not a universal quality judgment about the models.

### 2026-05-01 frontier smoke reinforced the case against `gpt-5.5` under the standard live policy

The newer cross-provider frontier smoke run under the normal shared live policy:
- `90s` execution turn timer
- `15s` placement timer
- placement `low`
- planning `medium`
- attack `medium`
- fortify `medium`
- card trade `low`

produced a sharper operational result than the earlier prompt-smoke probes alone.

Observed from the saved batch:
- `claude-opus-4-7`: `0` fallback calls
- `gemini-3.1-pro-preview`: `0` fallback calls
- `kimi-k2.6`: `0` fallback calls
- `gpt-5.5`: `4` fallback/error calls and `4` timed-out turns

Phase-level decision-time aggregate from that batch:
- `claude-opus-4-7`: about `3.03s` mean LLM call time
- `gemini-3.1-pro-preview`: about `4.68s`
- `kimi-k2.6`: about `3.27s`
- `gpt-5.5`: about `7.64s`

Interpretation:
- `gpt-5.5` still produced strategically legible plans
- the problem was not gross strategic confusion
- the problem was repeated wall-clock stress inside a synchronous turn loop
- end-of-turn attack and fortify calls were the main failure points

This matters because the repo's research question is not "which model sounds smartest in a single offline prompt". It is "which models can play well inside a bounded synchronous multi-call game loop".

Decision:
- do not treat `gpt-5.5` as the default OpenAI frontier representative for future cross-provider live-turn tournaments under the standard `90s / 15s` policy
- treat `gpt-5.4-medium` as the current best OpenAI default candidate for that specific deployment condition unless later tracked artifacts overturn it

Evidence:
- [2026-05-01_cross-provider-frontier-smoke.md](experiment-suites/2026-q2-strategic-tests/2026-05-01_cross-provider-frontier-smoke.md)

### Separate planning time is now an explicit experimental condition

The engine now supports an isolated pre-turn planning timeout via `planning_time_limit_seconds`.

Behavior:
- pre-turn planning can run under its own hard timeout
- that planning prompt now happens before the shared execution turn timer starts
- placement, attack, fortify, and card trade still share the normal execution timer

Why this matters:
- it lets us test a different research condition: "best strategic live play with bounded deliberate planning" rather than only "best low-latency fully synchronous play"
- it separates planning-quality questions from repeated in-turn action-latency questions

Related change:
- the repo now has a `live_turn_frontier_strategic` preset that:
  - uses `gpt-5.4` as the OpenAI execution model
  - uses `gpt-5.5` as an OpenAI planning-only override for the isolated pre-turn planning prompt
  - keeps Gemini on `gemini-3.1-pro-preview` with `high` planning and `medium` execution phases
  - keeps Kimi execution thinking disabled, but enables Kimi thinking on the isolated planning prompt only
  - gives planning an isolated `90s` timeout by default
  - uses `medium` placement / attack / fortify
  - uses `high` planning
  - enables provider thinking where supported

The engine also now supports planning-only client overrides at the `AgentSpec` layer. This means one provider/model can answer the isolated planning prompt while a different default client handles the repeated execution prompts in the same turn.

Methodological caution:
- results from `live_turn_frontier_strategic` are not directly comparable to the strict historical `live_turn_frontier` smoke runs
- the planning budget is a real condition change, not just a prompt tweak

## Experiments We Can Run Now

These are sensible near-term experiments with the current repo state.

### 1. OpenAI live-turn baseline series

Suggested format:
- `gpt-5.5` vs `gpt-5.4` vs `gpt-4.1`
- `3` to `5` games
- no between-game learning
- normal timing policy

Purpose:
- establish a clean post-fix OpenAI baseline
- verify that `gpt-4.1` now behaves normally in the real game loop

### 2. Provider smoke series

Suggested format:
- one short game each for OpenAI, Anthropic, and Gemini candidate rosters
- strict output/latency inspection

Purpose:
- verify prompt compatibility and runtime stability before cross-provider leagues

### 3. Representation benchmark

Suggested format:
- fixed board states
- same model
- current compact prompt vs alternatives

Purpose:
- measure comprehension, legality, latency, and token cost before changing the default state format again

### 4. Cheap reasoning-mode arena

Suggested format:
- `gpt-5.4-nano` or another low-cost model
- `none/low/medium/high`

Purpose:
- isolate how much extra reasoning effort helps in this domain before paying for expensive models

### 5. Cross-provider no-learning mini league

Suggested format:
- `3` players or `4` players
- `3` to `5` games
- no between-game adaptation

Purpose:
- get a first clean comparison of baseline strategic play across providers without the extra complexity of memory and tool building

## Issues That Need Attention Now

These are the current blockers or high-value gaps.

### High priority

- Add more scripted agent archetypes for offline diversity and long-run soak tests.
- Add a cheap cross-provider smoke suite for prompt/output compatibility.
- Re-run the OpenAI live baseline after the `gpt-4.1` reasoning fix.
- Decide and document the default "live-turn-safe" model roster.
- Refactor experiments into clearer declarative configs before starting serious leagues.

### Medium priority

- Add provider canaries for Anthropic and Gemini to match the OpenAI canary.
- Benchmark alternative state representations and prompt packs.
- Improve batch-level reporting so every experiment automatically produces summary plots and text analysis.

### Lower priority but important

- Formalize between-game learning rules before attempting adaptation leagues.
- Expand research calibration of the observable-strategy rubric on live games.

## Future Direction: Non-LLM Risk Engine

This project should eventually support both LLM agents and explicit algorithmic Risk agents.

### Goal

Use the same game engine and experiment harness as a testbed for:
- LLM players
- scripted heuristic players
- search/planning engines
- future self-play Risk engines

### Cleanest short-term path

The cleanest near-term route is to preserve the current game loop and swap in a non-LLM decision source behind the same player-facing interface.

Practical options:
- implement a local client that satisfies the same `get_chat_completion(...)` contract and returns parser-compatible moves
- create a non-LLM `PlayerAgent` sibling that bypasses prompt generation entirely and returns structured moves
- define a new decision-policy interface and have both `PlayerAgent` and future engine agents implement it

### Recommended architecture direction

The long-term cleaner design is:
- keep `GameMaster` responsible only for rules, turn flow, legality, and state transitions
- separate decision-making behind an explicit policy/agent interface
- allow policies to be backed by:
  - LLM prompts
  - scripted heuristics
  - local search
  - self-play training artifacts

### Why this matters

That architecture would let this repo become:
- a scientific test harness for LLM strategic behavior
- a regression environment for a future Risk engine
- a benchmark arena where LLMs and explicit algorithms can be compared directly

### Suggested staged path

1. Add more non-LLM scripted archetypes in the main codebase, not only tests.
2. Introduce a general decision-policy abstraction so the game loop is no longer conceptually tied to LLM prompts.
3. Build a first heuristic engine player that reasons over the structured game state directly.
4. Add self-play experiment support for non-LLM agents.
5. Only later attempt a more ambitious search or learning engine.

## Notes For The Article

These points are likely worth preserving for the final write-up.

- A stronger general model is not automatically a better live-game agent.
- Runtime fit matters: latency, output reliability, and turn-budget compliance are part of strategic usability.
- Some failures that look like "bad strategy" are really interface failures or runtime incompatibilities.
- The experiment platform needs to distinguish:
  - model capability
  - prompt quality
  - legality scaffolding
  - runtime latency
  - provider/API behavior
- Excluding a model such as `gpt-5.5-pro` can be methodologically correct when the live-play setting requires bounded synchronous decision-making and the model cannot reliably satisfy that constraint.

## 2026-04-27 Readiness Sweep

Before starting the first scored experiment batch, the repo was updated with two readiness-oriented pieces of infrastructure:

- per-game `game_manifest.json` files
- a fixed live `run_prompt_smoke_suite.py` preflight

The manifest addition matters because prompt/response logs alone are not enough for retroactive analysis. A saved game now has:
- `game_manifest.json`
- `turn_summary_turn_N.json`
- `llm_interactions/...`

That means later analysis can reconstruct:
- exact rules and timers
- player roster and provider/model assignments
- per-call prompts, raw responses, errors, and fallback usage
- per-turn parsed actions and board outcomes

### Smoke-suite result summary

The first readiness sweep used the real phase prompts from `PlayerAgent` against the candidate roster and validated outputs with the real engine legality checks.

#### Clean passes

These models cleared the smoke suite cleanly in the current setup:
- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-4.1`
- `claude-sonnet-4-6` in standard mode, without forcing Anthropic extended thinking

Interpretation:
- the current baseline prompt pack is operationally sound for these models
- they are reasonable candidates for scored synchronous experiments under the current timers

#### Important failures or cautions

`claude-sonnet-4-6` with forced thinking enabled failed completely in an early smoke pass, but this turned out to be a client-setting issue rather than a prompt issue.

Observed error:
- Anthropic returned `400 invalid_request_error` with `thinking.adaptive.effort: Extra inputs are not permitted`

Practical conclusion:
- Anthropic should currently be treated as live-turn-safe in standard mode
- Anthropic extended-thinking mode still needs a separate client/API-shape verification before we use it in scored live-turn experiments

`gemini-3.1-pro-preview` was mixed:
- pre-turn planning: valid
- troop placement: valid
- attack: valid
- fortify: fallback after provider read timeout near the full turn budget
- initial placement: timed out at the 15-second placement budget
- both card-trade prompts: valid

Practical conclusion:
- Gemini is not yet cleanly live-turn-safe under the current fixed timing policy
- the issue is not total prompt incompatibility, but timing reliability on specific phases

`kimi-k2.6` surfaced a more severe operational issue:
- before the timeout hardening, a smoke run could stall silently mid-suite
- after generalizing the hard worker-process timeout to all providers, the run completed
- Kimi then showed:
  - pre-turn planning fallback after roughly the full turn budget
  - initial placement fallback at 15 seconds
  - troop placement fallback at 15 seconds
  - attack, fortify, and both card-trade prompts were valid, but relatively slow

Practical conclusion:
- Kimi is not yet live-turn-safe under the current timing policy
- this is a meaningful experimental result, not just a parser bug

### Current provisional live-turn-safe roster

Based on the current readiness sweep:

Safe enough to score now:
- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-4.1`
- `claude-sonnet-4-6` in standard mode

Not yet safe enough for scored synchronous experiments under the current protocol:
- `gpt-5.5-pro`
- `gemini-3.1-pro-preview`
- `kimi-k2.6`

Interpretation rule:
- if a model cannot reliably satisfy the shared turn-budget policy, that is part of the result
- we should not silently relax the rules per provider without documenting that as a different deployment condition

### 2026-04-27 Provider Follow-Up: Opus, Gemini, and Kimi

I then did a second provider-specific validation pass, because the first sweep had mixed Gemini and Kimi results and I wanted to test the exact "smartest model per provider" candidates before any scored games.

#### Claude Opus 4.7

The first `claude-opus-4-7` failure was a client bug, not a model problem.

Observed failure:
- Anthropic returned `` `temperature` is deprecated for this model. ``

Fix:
- The Anthropic client now omits `temperature` for `claude-opus-4-7`.

After that fix, Opus 4.7 cleared the full prompt smoke suite cleanly in standard mode:
- planning: about `5.1s`
- initial placement: about `3.0s`
- troop placement: about `4.4s`
- attack: about `3.7s`
- fortify: about `3.8s`

Artifacts:
- [clean Opus/Gemini/Kimi smoke run](../game_results/prompt_smoke_runs/game__2026-04-27_14-47-34/prompt_smoke_summary.md)

I also verified the thinking-enabled path after fixing the client. The original adaptive-thinking configuration was wrong for Opus 4.7 because Anthropic rejected `thinking.adaptive.effort`. I changed the client to send adaptive thinking without an effort field for Opus 4.7.

Result:
- thinking-enabled Opus 4.7 is also live-turn-viable
- the full smoke probe finished with zero fallbacks
- timings were slower than standard mode but still within budget:
  - planning: about `7.1s`
  - placement: about `8.3s` and `11.0s`
  - attack: about `13.2s`

Artifact:
- [Opus thinking-enabled viability probe](../game_results/model_probes/anthropic_thinking_viability/game__2026-04-27_14-59-34/anthropic_opus_47_thinking_probe.json)

Practical conclusion:
- `claude-opus-4-7` is now a real candidate for scored synchronous play
- standard mode is the faster baseline
- adaptive thinking is usable, but it should be treated as a deliberate experimental condition rather than the default

#### Gemini

The original question was why I used `gemini-3.1-pro-preview`.

The answer:
- I initially used it because it was the highest-end currently visible Google Pro model in the live model surface
- the early timeout did **not** prove the model was incapable of playing Risk; it only proved that one live-turn run was unstable

Follow-up results:
- `gemini-2.5-pro` passed the full smoke suite cleanly
- `gemini-3.1-pro-preview` then passed the full smoke suite cleanly twice in a row

Measured timings from the clean runs:
- `gemini-2.5-pro`: slower, especially on attack/fortify (`~14s`)
- `gemini-3.1-pro-preview`: faster in the later clean runs and within the live-turn budgets

Artifacts:
- [multi-provider clean smoke run](../game_results/prompt_smoke_runs/game__2026-04-27_14-47-34/prompt_smoke_summary.md)
- [Gemini 3.1 repeat smoke run](../game_results/prompt_smoke_runs/game__2026-04-27_15-00-44/prompt_smoke_summary.md)

Practical conclusion:
- if we want the strongest currently visible Google candidate, use `gemini-3.1-pro-preview`
- if we want the less preview-dependent fallback, keep `gemini-2.5-pro`
- the earlier preview failure should be treated as operational noise, not as evidence of weak reasoning

#### Kimi K2.6

Kimi turned out to be the clearest settings-sensitive case.

With thinking disabled:
- full smoke suite passed cleanly
- per-phase timings were mostly in the `1s` to `4s` range

With thinking enabled:
- planning timed out near the full turn budget
- both placement phases hit the `15s` placement timeout
- attack also timed out
- total probe time ballooned to over `380s`

Artifact:
- [Opus + Kimi setting probe](../game_results/model_probes/live_turn_setting_probes/game__2026-04-27_14-51-19/live_turn_setting_probe_results.json)

Practical conclusion:
- `kimi-k2.6` is live-turn-safe only with thinking disabled
- thinking-enabled Kimi is not suitable for synchronous Risk play under the current rules

### Updated Live-Turn-Safe Roster

After the follow-up pass, the current provider candidates are:
- OpenAI: `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-4.1`
- Anthropic: `claude-opus-4-7` in standard mode as the default candidate; adaptive thinking is also viable if we explicitly want to test it
- Google: `gemini-3.1-pro-preview` as the chosen Google candidate for the main experiment program
- Moonshot: `kimi-k2.6` with thinking disabled

Still excluded from synchronous play:
- `gpt-5.5-pro`

### 2026-04-27 Batch Runner Layer

To reduce token waste and avoid treating the chat itself as an experiment dashboard, the repo now has a small experiment batch layer:
- `scripts/run_experiment.py`
- `scripts/experiment_status.py`
- `scripts/experiment_summary.py`

Design decision:
- long experiments should be launched once
- status should be read from `experiment_status.json`
- aggregate results should be read from `experiment_summary.json` / `experiment_summary.md`
- the agent should not repeatedly tail raw logs unless there is an actual failure to debug

This is an engineering workflow decision, but it also matters methodologically:
- it reduces the risk of duplicate runs, accidental interruption, or inconsistent manual bookkeeping
- it makes the experiment folder the canonical source of truth for what happened

The tracked folder structure for these runs now lives under:
- `game_results/experiments/`

### 2026-05-02 shared artifact audit clarified what is actually complete

On `2026-05-02`, we audited the shared experiment store rather than relying on memory from prior machines or chats.

Completed shared batches currently present:
- `mini_reasoning_2`
- `mini_medium_vs_high_300s_16`
- `frontier_smoke`
- `frontier_strategic_smoke`

Not found in the shared completed artifacts:
- `openai_generation_ladder`
- `openai_size_ladder`
- `openai_mini_high_strategic_hybrid`

Why this matters:
- future planning should treat those three runs as still pending unless their artifacts are restored from another machine
- we should not talk ourselves into conclusions that are not backed by the shared experiment store

### 2026-05-02 completed-batch interpretation

The completed shared runs support the following working conclusions:

- `gpt-5.4-mini-medium` is the best current live-turn setting on the mini line
- `gpt-5.4-mini-low` is the best efficiency fallback on the mini line
- `gpt-5.4-mini-high` is not justified for synchronous scored play even when given much more time
- `gpt-5.5-medium` is too slow for the strict cross-provider `90s / 15s` frontier condition
- `gpt-5.4-medium`, not `gpt-5.5-medium`, is the current OpenAI default for strict synchronous cross-provider live play

Strategic-frontier caveat:
- the completed `frontier_strategic_smoke` batch was an engineering pilot, not a clean research result
- that run used the earlier `60s` isolated planning budget
- `kimi-k2.6` repeatedly timed out in planning at `60s`
- `gemini-3.1-pro-preview` later hit daily-quota `429` failures mid-game, which contaminated the aggregate Gemini metrics

Operational consequence:
- treat the strategic pilot as architecture/debugging evidence, not as a publishable provider ranking
- keep the later move to `90s` isolated planning for the strategic preset

### 2026-05-02 strategic full-batch block

The first full `16`-game strategic frontier attempt failed immediately at `0 / 16` games because Gemini daily quota was exhausted.

Artifact:
- `/shared-game-results/experiments/experiment__2026-05-01_21-52-42__frontier_strategic_full_16`

Interpretation:
- this was a provider quota/infrastructure block, not a meaningful experimental outcome
- do not count that folder as a completed cross-provider strategic comparison

### 2026-05-04 combined generation ladder result: `gpt-5.1` is the current OpenAI live-turn baseline

We combined two completed `16`-game strategic generation-ladder replicates into one `32`-game blocked analysis:

- `/shared-game-results/experiments/experiment__2026-05-02_09-00-55__openai_generation_ladder_541_strategic_16`
- `/shared-game-results/experiments/experiment__2026-05-03_07-17-54__openai_generation_ladder_541_strategic_16_rep2`

Tracked note:
- [OpenAI Generation Ladder Strategic 32](experiment-suites/2026-q2-strategic-tests/2026-05-04_openai-generation-ladder-541-strategic-32.md)

Headline result:
- `gpt-5.1`: `18 / 32` wins
- `gpt-5.2`: `7 / 32`
- `gpt-4.1`: `4 / 32`
- `gpt-5.4`: `3 / 32`

Primary win benchmark:
- winner-label permutation omnibus on wins: `p = 0.000485`
- Holm-corrected pairwise support:
  - `gpt-5.1 > gpt-5.4`
  - `gpt-5.1 > gpt-4.1`
- `gpt-5.1` vs `gpt-5.2` was **not** significant after Holm correction on win-only tests

Secondary territory benchmark:
- `gpt-5.1` mean final territories: `19.38`
- `gpt-5.2`: `9.53`
- `gpt-5.4`: `7.09`
- `gpt-4.1`: `6.00`

Operational explanation:
- `gpt-5.1` did **not** win by having the best strategic rubric score; `gpt-5.2` slightly led there
- `gpt-5.1` won by converting turns into successful attacks and territory better than the others
- `gpt-5.4` was the slowest model in the important repeated phases and suffered severe placement/attack timeout pressure

Why this matters:
- the earlier working assumption that `gpt-5.4-medium` was the default next OpenAI candidate is no longer the best repo-level conclusion for the strategic live-turn condition
- the current working OpenAI baseline for strategic live-turn play should be `gpt-5.1`
- the best current planning-only hybrid candidate is `gpt-5.2` over `gpt-5.1` execution

Important framing correction:
- the broad all-pairs Holm family across all `6` unordered comparisons is stricter than the actual follow-up question that motivated the second replicate
- after the first `16` games, the main unresolved issue was whether `gpt-5.1 > gpt-5.2`
- under the narrower `gpt-5.1`-vs-rest Holm family that matches that follow-up question, the combined `32` games do support `gpt-5.1 > gpt-5.2` on wins

Practical conclusion:
- it is still correct to say that the broadest all-pairs family is more conservative
- but for the actual experimental sequence run here, the combined evidence should be read as reinforcing the initial `gpt-5.1 > gpt-5.2` signal rather than leaving it fully unresolved

### 2026-05-04 planner-only hybrid showdown was inconclusive

We then ran the planner-only hybrid ablation:

- `/shared-game-results/experiments/experiment__2026-05-03_20-35-06__openai_51_execution_hybrid_planning_showdown_16`

Tracked note:
- [OpenAI 5.1 Execution Hybrid Planning Showdown](experiment-suites/2026-q2-strategic-tests/2026-05-04_openai-51-execution-hybrid-planning-showdown.md)

Roster:
- `gpt-5.1-full`
- `gpt-5.5-plan / gpt-5.1-exec`
- `gpt-5.4-plan / gpt-5.1-exec`
- `gpt-5.2-plan / gpt-5.1-exec`

Headline win result:
- `gpt-5.2-plan / gpt-5.1-exec`: `5 / 16`
- `gpt-5.1-full`: `4 / 16`
- `gpt-5.5-plan / gpt-5.1-exec`: `4 / 16`
- `gpt-5.4-plan / gpt-5.1-exec`: `3 / 16`

Primary inference:
- winner-label permutation omnibus: `p = 0.985`
- no pairwise win test separated any variant from any other

Interpretation:
- this batch is almost perfectly compatible with equal win probabilities
- the planner-only effect, if real, is much smaller than the earlier full-stack generation differences
- `gpt-5.2` planning looked slightly best descriptively
- `gpt-5.5` planning remained fully plausible and was not beaten decisively
- `gpt-5.4` planning was the weakest descriptive option, but not in a way that supports a strong win-based claim at this sample size

Prior-sensitive read:
- if the prior is “all planner variants are equal once `gpt-5.1` execution is fixed,” this batch gives no reason to move far away from that view
- if the prior is “`gpt-5.5 > gpt-5.4 > gpt-5.2 > gpt-5.1`,” this batch does not support that order either

Practical consequence:
- do not claim that `gpt-5.2` is a proven better planner than `gpt-5.5`
- if the planner choice matters, resolve it with a larger direct playoff rather than with broader mixed planner rosters

### 2026-05-04 strategic provider roster now uses `gpt-5.1` execution and `gpt-5.5` planning

- the current cross-provider strategic preset now defaults to `gpt-5.1` for execution and `gpt-5.5` for the isolated planning phase
- rationale: the `32`-game OpenAI generation ladder established `gpt-5.1` as the strongest full-stack live-turn OpenAI model, while the later planner-only showdown did not provide strong evidence to displace `gpt-5.5` as the planning override
- added `configs/experiments/2026_q2_cross_provider_frontier_strategic.json` as the current frozen provider roster
- added `scripts/experiment_commands.sh` and `scripts/run_listed_experiment.sh` so experiment launches can be stored as numbered command lines instead of repeatedly typing long `make run-experiment ...` strings

### 2026-05-04 agent policy update: ambiguity, simplicity, and surgical scope

- `AGENTS.md` now explicitly requires four repo-level agent behaviors:
  - think before coding and surface ambiguity instead of guessing
  - prefer the minimum sufficient implementation
  - keep changes surgical and avoid unrelated cleanup
  - turn vague instructions into concrete, testable targets before editing code

### 2026-05-04 strategic cross-provider retry is invalid

- `/shared-game-results/experiments/experiment__2026-05-04_11-33-15__frontier_strategic_full_16`
- the trial completed `10` games and then failed during initial troop placement with `ValueError: Invalid territory assignment`
- root cause 1: single-move initial-placement parsing could apply more than one `|||Territory, 1|||` block from one response
- root cause 2: OpenAI quota exhaustion started in game `9` and heavily contaminated games `9+`
- the batch should be treated as invalid rather than partially salvageing later subsets
- tracked note: [Cross-Provider Frontier Strategic Full 16: Invalid Trial](experiment-suites/2026-q2-strategic-tests/2026-05-04_cross-provider-frontier-strategic-full-invalid.md)

### 2026-05-05 strategic cross-provider retry 2 salvage plan

- `/shared-game-results/experiments/experiment__2026-05-04_21-00-11__frontier_strategic_full_16_retry_2`
- this rerun completed all `16` games after the setup parser fix, so the earlier placement corruption is no longer the issue here
- Anthropic credits ran out during games `7-12`, contaminating only the `claude-opus-4-7` side of that window
- no Gemini quota failures were observed in this rerun
- games `13-16` look clean again after the Anthropic refill
- salvage plan:
  - keep games `1-6`
  - keep games `13-16`
  - drop games `7-12`
  - append a clean `6`-game top-up using `configs/experiments/2026_q2_cross_provider_frontier_strategic_topup_6.json`
  - combine the retained `10` games plus the clean top-up to form the final balanced `16`-game provider experiment
- tracked note: [Cross-Provider Frontier Strategic Full 16 Retry 2: Salvage Plan](experiment-suites/2026-q2-strategic-tests/2026-05-05_cross-provider-frontier-strategic-retry-2-salvage-plan.md)

### 2026-05-06 balanced cross-provider strategic result favors Gemini

The clean `10`-game subset from `frontier_strategic_full_16_retry_2` was combined with the clean `6`-game `frontier_strategic_topup_6` batch into a reconstructed balanced provider series:

- `/shared-game-results/experiment_series/frontier_strategic_full_16_salvaged`

That merged series restores perfect seat balance by giving every provider `4` appearances in each seat.

Final win counts:
- `gemini-3.1-pro-preview`: `10`
- `claude-opus-4-7`: `3`
- `gpt-5.1`: `2`
- `kimi-k2.6`: `1`

Important interpretation:
- Gemini is the current strongest provider representative under this strategic live `90 / 90 / 15` condition
- Claude is operationally cleaner than GPT-5.1, but still wins much less often than Gemini
- GPT-5.1 remains strategically credible but continues to lose ground through higher timeout/fallback pressure

Tracked note:
- [Cross-Provider Frontier Strategic 16: Salvaged Balanced Result](experiment-suites/2026-q2-strategic-tests/2026-05-06_cross-provider-frontier-strategic-16-salvaged.md)

### 2026-05-06 roadmap update after the balanced provider result

The provider result changes the experimental priorities.

What is now resolved enough:
- `gpt-5.1` is the current OpenAI live-turn baseline
- the older short `gpt-5.5 / gpt-5.4 / gpt-4.1` baseline plan is no longer a high-value next step

What is now highest priority:
- implement quota/billing-aware pause and operator resume for long provider runs
- run one clean confirmatory replicate of the current strategic provider lineup

What is lower priority until that replicate exists:
- more OpenAI-only ladder cleanup
- broader representation or learning work that assumes the provider ranking is already stable
