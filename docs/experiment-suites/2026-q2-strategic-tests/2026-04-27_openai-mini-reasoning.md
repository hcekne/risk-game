# OpenAI Mini Reasoning 2

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `mini_reasoning_2`
- Preset: `openai_mini_reasoning`
- Raw local artifacts: `game_results/experiments/experiment__2026-04-27_22-29-27__mini_reasoning_2`
- Core files:
  - `experiment_manifest.json`
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`

## Research Question

Does reasoning level materially affect the strategic performance of `gpt-5.4-mini` in this Risk environment?

More precisely, this experiment should be framed as:
- which reasoning settings produce the strongest **usable synchronous live-turn agents** under a constrained timer regime?

It is **not** primarily an unconstrained strategic-ceiling test.

## Design

- Model family: `gpt-5.4-mini`
- Conditions:
  - `gpt-5.4-mini-none`
  - `gpt-5.4-mini-low`
  - `gpt-5.4-mini-medium`
  - `gpt-5.4-mini-high`
- Games: `16`
- Seats: `4-player`, seat-rotated
- Seat balance: each condition occupied each seat exactly `4` times
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - turn timer `120s`
  - placement timer `25s`

## Hypotheses

Primary endpoint:
- final territory share

Primary hypotheses:
- `H0`: reasoning level has no effect on final territory share; mean final territory share is equal across `none`, `low`, `medium`, and `high`.
- `H1`: at least one reasoning level differs in final territory share.

Supporting directional interpretation:
- if there is a useful reasoning benefit in this setup, we would expect `low` and/or `medium` to outperform `none`
- if additional reasoning remains operationally viable, we might expect `high` to outperform lower settings

## Statistical Method

Primary test:
- blocked permutation test on final territory share across all four conditions

Why this test:
- each game contains all four compared agents
- seat rotation balances order effects
- the design is repeated-measures by game rather than independent groups
- blocked nonparametric testing avoids stronger distributional assumptions than the data supports

Post-hoc testing:
- pairwise blocked permutation tests on final territory share
- Holm correction across the six pairwise comparisons

Supporting tests:
- exact binomial test on `medium` win count versus a uniform `25%` baseline
- exploratory blocked permutation tests on strategic rubric scores

## Core Result

The experiment rejects `H0`.

Primary omnibus result:
- blocked permutation test on final territory share: `p = 0.00014`

Interpretation:
- reasoning level clearly mattered in this setup
- the effect was not monotonic
- `medium` was best
- `low` was second
- `high` underperformed badly
- `none` was weakest on wins and board outcomes

The most defensible headline framing is:
- more reasoning helped up to a point
- beyond that point, additional reasoning became harmful because the agent was too slow to complete repeated in-turn decisions inside the live clock

## Descriptive Outcomes

Overall batch:
- games completed: `16 / 16`
- mean rounds: `10.44`
- mean elapsed time: `2499.24s`
- `12/16` games ended by `Territory Control 65%`
- `4/16` games ended by `Max Rounds Reached - Territory Control`

Win counts:
- `medium`: `11`
- `low`: `4`
- `high`: `1`
- `none`: `0`

Per-condition summary:

| Condition | Wins | Mean Final Territories | Mean Territory Share | Mean Turn Time (s) | Mean Fallbacks | Mean Placement Errors | Mean Strategic Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `none` | 0 | 4.19 | 0.0997 | 170.28 | 0.19 | 0.25 | 4.522 |
| `low` | 4 | 12.75 | 0.3036 | 253.65 | 0.06 | 0.19 | 4.763 |
| `medium` | 11 | 19.31 | 0.4598 | 675.90 | 1.06 | 0.56 | 4.830 |
| `high` | 1 | 5.75 | 0.1369 | 1399.00 | 18.88 | 16.38 | 4.263 |

Median final territories:
- `none`: `5`
- `low`: `11`
- `medium`: `26`
- `high`: `5`

## Post-Hoc Comparisons

Pairwise blocked permutation tests on final territory share, with Holm correction:

| Comparison | Mean Share Difference | Permutation p | Holm-Reject? |
| --- | ---: | ---: | --- |
| `medium > none` | `+0.3601` | `0.00113` | Yes |
| `medium > high` | `+0.3229` | `0.00147` | Yes |
| `low > none` | `+0.2039` | `0.00570` | Yes |
| `low > high` | `+0.1667` | `0.02987` | No |
| `high > none` | `+0.0372` | `0.07460` | No |
| `medium > low` | `+0.1562` | `0.21463` | No |

Main takeaways:
- `medium` was clearly better than `none`
- `medium` was clearly better than `high`
- `low` was clearly better than `none`
- `medium` was not cleanly separable from `low` at this sample size
- `low` and `high` were not cleanly separable after correction, even though their means differed materially

## Win-Rate Check

Supporting exact binomial test:
- `medium` wins: `11/16`
- one-sided p against `25%` win probability: `0.00029`

Interpretation:
- `medium` did not just edge out the others on mean territory share
- it also won far more often than chance would predict in a symmetric 4-player field

## Seat Effects

Seat exposure was perfectly balanced:
- every condition occupied seats `1` through `4` exactly `4` times

Overall seat means were not equal:
- seat `1`: `8.62`
- seat `2`: `12.69`
- seat `3`: `8.38`
- seat `4`: `12.31`

But this does not explain the main result:
- seat assignment was balanced across conditions
- `medium` won from all four seats
- `medium` was especially strong from seat `4`, but not only from seat `4`

## Game-Level Pattern

The batch was not a single-mode outcome:
- `low` won a few fast snowball games
- `medium` dominated most of the middle and late part of the batch
- `high` managed one max-round territory-control win
- `none` never converted into a win

Representative pattern:
- game 1: `low` won in `4` rounds
- games 2, 4, 5, 8, 10, 12, 13, 16: `medium` won by direct `65%` territory control
- games 6, 7, 15: `medium` also topped the board in max-round finishes
- game 11: `high` won only by max-round territory control, not by a clean territory-control sweep

## Operational Viability Findings

This experiment does not only measure abstract reasoning quality. It measures reasoning quality under a real live-turn budget.

That matters most for `high`.

`high` was not simply strategically worse. It was operationally fragile:
- mean fallback count: `18.88`
- mean placement errors: `16.38`
- mean turn time: `1399s`

Example failure mode:
- in [0069_troop_placement.json](../../../game_results/experiments/experiment__2026-04-27_22-29-27__mini_reasoning_2/llm_interactions/game__2026-04-28_05-53-35/gpt-5.4-mini-high/round_08/turn_0029/0069_troop_placement.json), `gpt-5.4-mini-high` hit the `25s` wall-clock limit on a troop-placement prompt and fell back to the engine's `Blank` response.

So the meaning of the result is:
- `high` under this protocol is not a good live-turn setting
- it over-spends reasoning budget often enough to hurt real game play

This is an important article point:
- stronger or deeper reasoning settings are not automatically better in a synchronous game environment
- they must still be operationally compatible with the time budget

## Timer Semantics

The timer behavior in this batch matters for interpretation.

Main-turn timer:
- `120s` total per normal turn
- shared across:
  - pre-turn planning
  - troop placement
  - all attack calls during that turn
  - fortify

Placement timer:
- `25s` wall-clock cap per placement prompt
- applies to:
  - initial setup placement calls
  - normal troop-placement prompts

Important nuance:
- the alternating initial setup phase is not one shared `120s` turn
- instead, each initial setup placement call is separately capped at `25s`

For normal turns:
- the turn timer starts before troop placement
- attack and fortify prompts do not have a separate small hard cap
- they are bounded by whatever turn budget remains at that point in the turn
- the engine also keeps a small internal safety margin before the turn fully expires

Practical implication:
- if a model spends `20-40s` on one attack decision, that time comes out of the same `120s` turn budget that must also cover later attacks and fortification
- so a model can be strategically capable in principle but still fail badly as a synchronous live-turn player if it spends too much time per repeated action

## Phase-Level Diagnostic

The deeper log review shows that `high` did not merely have “a few” timeouts.

Phase-level fallback and timeout rates for `gpt-5.4-mini-high`:

| Phase | Total Calls | Fallbacks | Timeouts | Fallback Rate |
| --- | ---: | ---: | ---: | ---: |
| `initial_troop_placement` | 379 | 71 | 71 | 18.7% |
| `troop_placement` | 330 | 191 | 188 | 57.9% |
| `attack` | 518 | 103 | 85 | 19.9% |
| `fortify` | 55 | 8 | 7 | 14.5% |
| `pre_turn_planning` | 163 | 0 | 0 | 0.0% |

The key point is that pre-turn planning was not the main problem.

The real problem was repeated in-turn action selection:
- troop placement was the worst phase by far
- attack was the second major failure mode
- initial setup placement still failed a lot, though much less than normal troop placement

For comparison, `medium` was far more operationally stable:

| Phase | `medium` Fallback Rate |
| --- | ---: |
| `initial_troop_placement` | 0.0% |
| `troop_placement` | 4.2% |
| `attack` | 1.0% |
| `fortify` | 0.7% |
| `pre_turn_planning` | 0.0% |

## Latency Regime Difference

Looking only at successful calls, `high` still operated in a much slower regime than `medium`.

Successful-call latency percentiles for `high`:

| Phase | p50 | p75 | p90 | p95 |
| --- | ---: | ---: | ---: | ---: |
| `initial_troop_placement` | 8.89s | 15.98s | 21.16s | 23.36s |
| `troop_placement` | 15.41s | 19.94s | 23.65s | 24.75s |
| `attack` | 10.95s | 22.37s | 35.48s | 41.60s |
| `fortify` | 8.01s | 12.43s | 27.33s | 33.33s |
| `pre_turn_planning` | 6.58s | 10.42s | 18.43s | 24.58s |

Successful-call latency percentiles for `medium`:

| Phase | p50 | p75 | p90 | p95 |
| --- | ---: | ---: | ---: | ---: |
| `initial_troop_placement` | 3.18s | 4.84s | 8.78s | 10.48s |
| `troop_placement` | 8.89s | 13.42s | 19.24s | 23.60s |
| `attack` | 4.93s | 7.70s | 11.48s | 14.31s |
| `fortify` | 4.70s | 8.42s | 14.49s | 18.96s |
| `pre_turn_planning` | 3.91s | 5.12s | 6.96s | 8.08s |

The most important gap is attack:
- `medium` usually answered attack prompts quickly enough to string multiple attacks together in one turn
- `high` often spent so long on a single attack that it effectively cannibalized its own remaining turn budget

This explains why `high` can look coherent in planning but still play badly overall.

## Refined Interpretation Of `High`

The correct interpretation is not simply:
- `high` is strategically worse

The better interpretation is:
- `high` is a poor synchronous live-turn setting under this timer regime

This experiment therefore supports a narrower but stronger claim:
- in an online-Risk-style timed environment, `gpt-5.4-mini-high` is not operationally viable enough to compete well with `medium`

It does **not** yet prove:
- that `high` would remain worse if given much more time
- that `high` has lower strategic ceiling in an unconstrained or semi-asynchronous setting

## What This Means For Follow-Up Experiments

There are two different research questions available now, and they should not be conflated.

### Question A: What is the best setting for realistic synchronous live play?

For this question, the current experiment is already informative.

Conclusion:
- `medium` is best
- `low` is a strong efficiency option
- `high` is not suitable for realistic online-style timed play

This is the correct interpretation if the experiment is used as evidence about:
- live competitive play
- online-Risk-style turn clocks
- models acting as usable real-time game agents

If the article focuses on usable live agents, this may already be enough.

### Question B: Does `high` have a higher strategic ceiling if given more time?

For this question, the current batch is not enough.

A justified follow-up would be:
- compare `medium` and `high` directly
- increase both the full-turn timer and placement timer
- keep prompts and parser fixed

The justification is strong because the current logs show that `high` was frequently budget-constrained rather than simply making obviously bad legal moves.

However, simply increasing placement time alone is not enough.

Why:
- troop placement was the biggest single failure mode
- but attack timing was also a major problem
- many `high` turns likely failed because repeated `10-40s` attack calls exhausted the shared `120s` turn timer

So a meaningful follow-up would need:
- more placement time
- and more full-turn time

## Recommended Next Experiment For `High` vs `Medium`

The most interesting next test is probably **not** rerunning `none/low/medium/high` with larger timers.

A better focused follow-up is:
- compare `medium` vs `high`
- use only those two profiles
- run under a more generous timer regime

### Recommended roster size

Use `4` players:
- `2` copies of the `medium` profile
- `2` copies of the `high` or hybrid profile

Why `2 vs 2` rather than `1 vs 3`:
- a `1 high + 3 medium` setup is asymmetric and hard to interpret
- board politics and target selection can dominate the result
- `2 vs 2` keeps the field balanced while still preserving free-for-all play
- each game then contains both compared conditions twice, which reduces single-game variance

Recommended analysis unit:
- compute per-game average final territory share by profile
- compare the two profile averages across games with a paired / blocked test

That is cleaner than treating one isolated `high` copy as if it were directly comparable to three `medium` copies in the same game.

Two good variants:

1. `High` vs `Medium` under larger timers
- goal: test whether `high` recovers when its time-budget constraint is relaxed
- suggested lineup:
  - `medium-a`
  - `medium-b`
  - `high-a`
  - `high-b`
- suggested timer regime:
  - `240s` full turn
  - `50s` placement
- suggested rollout:
  - first a `4`-game operational probe
  - then `16` scored games if fallbacks drop to an acceptable level

2. Hybrid `High-Strategic` vs `Medium`
- use `high` for planning and attack
- use `medium` or `low` for placement, fortify, and card trade
- goal: test whether extra reasoning helps on the strategically rich phases without letting administrative phases dominate the result
- suggested lineup:
  - `medium-all-a`
  - `medium-all-b`
  - `high-strategic-a`
  - `high-strategic-b`
- suggested timer regime:
  - start with the original constrained environment (`120s` turn, `25s` placement)
  - if attack-time collapse persists, relax only the full-turn budget modestly and document that change explicitly

That second design may be the best scientific next step if the real question is:
- does deeper reasoning help where strategy matters most?

## Practical Summary For The Article

This experiment supports a strong and publication-worthy claim:
- in a constrained synchronous game environment, additional reasoning improves play only up to the point where latency begins to dominate execution

Put differently:
- `none` and `low` were faster but shallower
- `medium` hit the best balance of depth and speed
- `high` likely crossed the line where more thinking was no longer useful because it interfered with timely action selection

That is a very different claim from:
- `high` is inherently less strategically capable

The current evidence supports the first claim strongly, and leaves the second claim open.

## Strategic Rubric Result

Exploratory strategic-rubric means:
- `medium`: `4.830`
- `low`: `4.763`
- `none`: `4.522`
- `high`: `4.263`

Blocked permutation omnibus test on strategic rubric score:
- `p = 0.00002`

Interpretation:
- the observed strategic trace quality also differed across reasoning levels
- but the rubric separated `medium` and `low` much less sharply than the board outcomes did

That suggests:
- the rubric is useful
- but hard game outcomes still capture important things the rubric underweights, especially tempo conversion and timeout-driven disruption

## Interpretation

The cleanest conclusion is:
- reasoning level clearly mattered
- the relationship was not monotonic
- `medium` was the strongest overall setting
- `low` was a strong second-best and may be the best efficiency setting
- `high` was harmful in this live-turn setup
- `none` was operationally stable but strategically too weak

In short:
- more reasoning helped up to `medium`
- pushing to `high` hurt performance because the live-turn environment penalized overthinking

## Practical Recommendation

For future `gpt-5.4-mini` live-turn experiments in this repo:
- use `medium` when maximizing strength is the goal
- use `low` when speed/cost/operational reliability matter more
- do not use `high` for synchronous scored play without first changing the timing model or placement protocol

## Caveats

This batch is strong enough to support a real conclusion, but it still has limits:
- `16` games is good for an initial blocked comparison, not the final word
- `medium` vs `low` did not separate cleanly after correction
- `high` was partially degraded by timeout/fallback behavior, so the result is about live-turn usefulness, not pure unconstrained reasoning ability
- the experiment uses one engine version, one prompt pack, and one timer regime

## Follow-Up

The most useful follow-up experiments are:
- rerun this reasoning ladder with a larger sample if `medium` vs `low` becomes a headline claim
- repeat the reasoning-ladder concept on a second OpenAI model line
- run the formal recovery test in [2026-04-28_openai-mini-high-vs-medium-recovery-plan.md](2026-04-28_openai-mini-high-vs-medium-recovery-plan.md)
- compare the best viable reasoning setting from OpenAI against Anthropic, Gemini, and Kimi in the cross-provider championship
