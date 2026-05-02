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
