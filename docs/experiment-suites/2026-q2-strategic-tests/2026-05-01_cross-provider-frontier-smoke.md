# Cross-Provider Frontier Smoke 2

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `frontier_smoke`
- Preset: `live_turn_frontier`
- Raw local artifacts: `/shared-game-results/experiments/experiment__2026-05-01_09-03-34__frontier_smoke`
- Core files:
  - `experiment_manifest.json`
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`

## Research Question

Does the locked cross-provider frontier roster complete cleanly under the standard synchronous live-turn policy, and do any of the candidates show clear operational stress even if their high-level plans look strategically coherent?

This was a runtime-viability smoke test first and a ranking exercise second.

## Design

- Conditions:
  - `gpt-5.5`
  - `claude-opus-4-7`
  - `gemini-3.1-pro-preview`
  - `kimi-k2.6`
- Games: `2`
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - shared execution turn timer `90s`
  - placement timer `15s`
  - placement reasoning `low`
  - planning reasoning `medium`
  - attack reasoning `medium`
  - fortify reasoning `medium`
  - card-trade reasoning `low`

## Hypotheses

Primary operational question:
- `H0`: the locked frontier roster is cleanly usable under the `90s / 15s` synchronous policy
- `H1`: at least one roster member is operationally stressed enough that the roster should be reconsidered before a larger championship

Secondary descriptive question:
- if a model underperforms, is it because the strategic plans are weak, or because the runtime cannot reliably complete the turn inside the clock?

## Core Result

The batch completed `2 / 2` games cleanly, but it did **not** support keeping `gpt-5.5` as the default OpenAI live-turn frontier representative under the shared `90s / 15s` policy.

Observed winners:
- game 1: `claude-opus-4-7`
- game 2: `gemini-3.1-pro-preview`

Operational read:
- `claude-opus-4-7`: clean
- `gemini-3.1-pro-preview`: clean
- `kimi-k2.6`: fast enough, but lower-quality tactical execution
- `gpt-5.5`: strategically legible, but too slow and timeout-prone for this live policy

Most important concrete evidence:
- `gpt-5.5` logged `4` fallback/error calls
- those fallbacks corresponded to `4` timed-out turns
- `gpt-5.5` had the slowest mean LLM call time in the batch: `7.64s`
- `claude-opus-4-7`, `gemini-3.1-pro-preview`, and `kimi-k2.6` all completed with `0` fallback calls

Interpretation:
- this was not a clean signal that `gpt-5.5` is strategically bad
- it **was** a clean signal that `gpt-5.5` is a poor runtime fit for synchronous `90s` turns with `15s` placement prompts

This smoke run therefore supports the working repo conclusion that `gpt-5.4-medium`, not `gpt-5.5-medium`, should be the default OpenAI candidate for the next cross-provider live-turn frontier tournament.

## Descriptive Outcomes

Batch summary:
- games completed: `2 / 2`
- mean rounds: `6`
- mean elapsed time: `1096.15s`

Win counts:
- `claude-opus-4-7`: `1`
- `gemini-3.1-pro-preview`: `1`
- `gpt-5.5`: `0`
- `kimi-k2.6`: `0`

Per-player summary:

| Player | Wins | Mean Final Territories | Mean Turn Time (s) | Mean Strategic Score | Mean Fallback Count | Mean Attack Errors | Mean Fortify Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `claude-opus-4-7` | 1 | 14.0 | 185.16 | 4.92 | 0.0 | 0.5 | 0.0 |
| `gemini-3.1-pro-preview` | 1 | 18.5 | 323.63 | 4.93 | 0.0 | 0.0 | 0.0 |
| `gpt-5.5` | 0 | 7.5 | 353.02 | 4.64 | 2.0 | 0.0 | 0.0 |
| `kimi-k2.6` | 0 | 2.0 | 234.18 | 4.87 | 0.0 | 0.0 | 0.5 |

Useful phase-level runtime aggregates from the saved turn summaries:

| Player | Mean LLM Call Time | Timed-Out Turns | Fallback/Error Calls |
| --- | ---: | ---: | ---: |
| `claude-opus-4-7` | `3.03s` | 0 | 0 |
| `gemini-3.1-pro-preview` | `4.68s` | 0 | 0 |
| `gpt-5.5` | `7.64s` | 4 | 4 |
| `kimi-k2.6` | `3.27s` | 0 | 0 |

The summary file's `mean_turn_time_seconds` should be read as total accumulated turn time per game, not literal wall-clock per-turn latency. The phase-level call timings above are the more useful operational measure.

## What The Models Actually Did

### `claude-opus-4-7`

Claude looked like the cleanest all-round live agent in this batch.

Observable behavior:
- continent-aware plans
- explicit avoidance of bad fronts
- coherent multi-step attack chains
- low runtime overhead

Representative plan style:
- reinforce the strongest realistic breakout point
- avoid giant enemy stacks
- take cheap connected territories rather than grind equal fights

The main blemish was one invalid attack where the model effectively targeted a territory it already owned. That was a tactical parsing mistake, not a general planning failure.

### `gemini-3.1-pro-preview`

Gemini produced the strongest tactical conversion in the batch.

Observable behavior:
- repeated clean attack chains
- no invalid actions
- no failed attacks in the aggregate summary
- no fallbacks
- explicit leader-targeting and elimination pressure

In the second game it produced the most decisive breakout of the batch and converted that into the win.

### `gpt-5.5`

The important distinction is:
- its plans were usually coherent
- its runtime fit was not

Examples of reasonable `gpt-5.5` plan style:
- identify one main stack
- name a plausible breakthrough chain
- preserve a clear fallback front if the chain stalls

But several turns hit hard wall-clock timeouts:
- fortify timeout at `3.74s`
- attack timeouts at `1.05s`, `7.10s`, and `10.48s`

Those fallbacks stopped attacks or skipped fortification even when the strategic outline was still sensible.

So the correct conclusion is not:
- "`gpt-5.5` cannot plan"

The correct conclusion is:
- "`gpt-5.5` cannot reliably finish synchronous live turns under this policy"

### `kimi-k2.6`

Kimi was fast enough but tactically rougher than Claude or Gemini.

Observable behavior:
- plans were often strategically legible
- execution produced more failed attacks than Claude or Gemini
- one invalid fortify attempted to move from a `1`-troop source territory

So Kimi remained usable, but not cleanly elite.

## Why `gpt-5.5` Lost Here

The saved traces do **not** support a simple "bad strategy" story.

Instead they support this chain:
1. `gpt-5.5` spends more wall-clock time per decision than the other candidates
2. that compounds over a full turn
3. attack and fortify calls near the end of the turn run into the hard timeout path
4. the engine falls back to a blank/stop response
5. the turn ends with a weaker board conversion than the plan originally aimed for

That matters because this repo evaluates synchronous live-turn play, not unconstrained offline planning.

## Decision

For the standard `90s` turn / `15s` placement live-turn regime:
- keep `live_turn_frontier` frozen as the historical smoke preset
- do **not** treat `gpt-5.5` as the default OpenAI frontier representative for future cross-provider championships
- treat `gpt-5.4-medium` as the next OpenAI candidate to carry forward for live frontier work

## Follow-On Recommendation

Two follow-ons are justified from this smoke run:

1. run the OpenAI generation ladder against the same live-turn policy if the artifact is not already tracked in the shared store
2. use the new higher-ceiling strategic preset for best-effort cross-provider play:
   - isolated planning timer
   - stronger planning reasoning
   - provider thinking enabled where supported

That second path is a different experimental condition from the strict historical `live_turn_frontier` smoke and should be analyzed separately.
