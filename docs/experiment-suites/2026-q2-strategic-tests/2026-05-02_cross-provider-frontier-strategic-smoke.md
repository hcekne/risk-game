# Cross-Provider Frontier Strategic Smoke

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `frontier_strategic_smoke`
- Preset: `live_turn_frontier_strategic`
- Raw local artifacts: `/shared-game-results/experiments/experiment__2026-05-01_20-51-42__frontier_strategic_smoke`
- Core files:
  - `experiment_manifest.json`
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`

## Research Question

Under the higher-ceiling strategic frontier condition, do the cross-provider candidates remain operationally usable when they get an isolated planning step before the shared live turn timer starts?

This was an engineering pilot first and a model-comparison run second.

## Design

- Conditions:
  - OpenAI execution: `gpt-5.4`
  - OpenAI planning override: `gpt-5.5`
  - Anthropic: `claude-opus-4-7`
  - Gemini: `gemini-3.1-pro-preview`
  - Moonshot: `kimi-k2.6`
- Games: `2`
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - isolated pre-turn planning timer `60s`
  - shared execution turn timer `90s`
  - placement timer `15s`
  - placement reasoning `medium`
  - planning reasoning `high`
  - attack reasoning `medium`
  - fortify reasoning `medium`
  - card-trade reasoning `low`

Important historical note:
- this pilot was run before the later repo change that raised the default strategic planning budget from `60s` to `90s`
- the results therefore apply to the earlier `60s planning + 90s execution + 15s placement` condition

## Core Result

The batch completed `2 / 2` games, but it did **not** produce a clean research-facing comparison.

Observed winners:
- game 1: `gemini-3.1-pro-preview`
- game 2: `claude-opus-4-7`

The problem is that game 2 was quota-contaminated:
- `gemini-3.1-pro-preview` hit repeated Gemini API `429 RESOURCE_EXHAUSTED` errors mid-game
- those provider failures inflated the batch summary with `61` Gemini fallback calls and `33` Gemini placement errors in that one game

That means the saved batch is useful as an engineering pilot, but not as a trustworthy headline model ranking.

## Descriptive Outcomes

Batch summary:
- games completed: `2 / 2`
- mean rounds: `9`
- mean elapsed time: `2384.51s`

Per-game outcomes:

### Game 1

- winner: `gemini-3.1-pro-preview`
- rounds: `6`
- final territories:
  - `gemini-3.1-pro-preview`: `28`
  - `gpt-5.4`: `10`
  - `kimi-k2.6`: `4`
  - `claude-opus-4-7`: `0`

Useful engineering signal:
- `gpt-5.4`: `6` fallback calls
- `kimi-k2.6`: `5` fallback calls
- `claude-opus-4-7`: `0`
- `gemini-3.1-pro-preview`: `0`

### Game 2

- winner: `claude-opus-4-7`
- rounds: `12`
- final territories:
  - `claude-opus-4-7`: `28`
  - `gpt-5.4`: `6`
  - `gemini-3.1-pro-preview`: `4`
  - `kimi-k2.6`: `4`

Contamination signal:
- `gemini-3.1-pro-preview`: `61` fallback calls
- `gemini-3.1-pro-preview`: `33` placement errors
- the recorded failures are repeated Gemini daily-quota `429` responses, not normal turn-budget overruns

## What The Pilot Still Taught Us

### `claude-opus-4-7`

Claude was the clean runtime baseline in this batch:
- `0` fallback calls across both games
- no placement, attack, or fortify error counts
- one win and stable execution throughout

Interpretation:
- Claude remained operationally strong under the strategic condition
- this batch did not expose a new Anthropic-specific runtime problem

### `gpt-5.4` with `gpt-5.5` planning

The OpenAI split architecture did produce strategically usable play, but the execution side still showed timing stress.

Observed failure pattern:
- repeated execution-side timeouts
- fallback spikes in both games
- especially attack and late-turn execution pressure rather than planning collapse

Interpretation:
- the OpenAI planning split was viable enough to test further
- but `gpt-5.4` execution was still under real pressure in repeated live actions
- this pilot did not overturn the repo conclusion that strict live play strongly favors `gpt-5.4-medium` over `gpt-5.5-medium` as the default one-model OpenAI representative

### `kimi-k2.6`

Kimi's main failure mode in this pilot was isolated planning latency.

Observed failure pattern:
- repeated `pre_turn_planning` wall-clock timeouts at the full `60s` planning cap

Interpretation:
- Kimi planning-only thinking was still too slow for the earlier `60s` strategic budget
- this was the direct reason the strategic preset was later revised to use `90s` isolated planning

### `gemini-3.1-pro-preview`

Gemini's batch summary looks much worse than its actual clean-play signal because the second game was interrupted by provider quota exhaustion.

Observed failure pattern:
- repeated `429 RESOURCE_EXHAUSTED` Gemini API failures
- these failures then propagated into planning, placement, attack, and fortify fallback counts

Interpretation:
- the game-2 Gemini collapse is not evidence of weak strategy
- it is evidence that quota exhaustion can invalidate a live cross-provider comparison mid-run

## Decision

Treat this batch as:
- a completed engineering pilot
- not a clean research-facing model comparison

Working decisions from this pilot:
1. do not use this batch's Gemini aggregate metrics as a capability signal
2. keep the later repo change that raises strategic isolated planning from `60s` to `90s`
3. require a real Gemini quota check before retrying the full strategic frontier batch

## Related Follow-Up

The first full strategic batch attempt failed immediately at `0 / 16` games because Gemini daily quota was already exhausted:
- `/shared-game-results/experiments/experiment__2026-05-01_21-52-42__frontier_strategic_full_16`

That failure should be treated as an infrastructure/runtime block, not as an experiment result.
