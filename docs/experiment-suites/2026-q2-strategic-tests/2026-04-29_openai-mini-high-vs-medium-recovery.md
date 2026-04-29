# OpenAI Mini High-vs-Medium Recovery

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `mini_medium_vs_high_300s_16`
- Preset: `openai_mini_medium_vs_high`
- Raw local artifacts: `game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16`
- Core files:
  - `experiment_manifest.json`
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`

## Research Question

Does `gpt-5.4-mini-high` recover against `gpt-5.4-mini-medium` when the live-turn budget is relaxed enough that repeated in-turn decisions are less likely to time out?

This was a wins-first recovery test, not a general strategic-ceiling test.

## Design

- Model family: `gpt-5.4-mini`
- Conditions:
  - `gpt-5.4-mini-medium-a`
  - `gpt-5.4-mini-medium-b`
  - `gpt-5.4-mini-high-a`
  - `gpt-5.4-mini-high-b`
- Games: `16`
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - turn timer `300s`
  - placement timer `50s`

## Hypotheses

Primary endpoint:
- game winner

Let:
- `X` = number of games won by the `high` side
- `n = 16`

Primary hypotheses:
- `H0: p <= 0.5`
- `H1: p > 0.5`

where `p` is the probability that a `high` player wins a game in this `2 high vs 2 medium` setup.

Primary test:
- exact one-sided binomial test with `X ~ Binomial(16, 0.5)` under `H0`

Pre-registered rejection rule:
- reject `H0` if the high side wins at least `12/16` games

## Core Result

The experiment does **not** reject `H0`.

Observed win split:
- `high`: `8/16`
- `medium`: `8/16`

Exact one-sided binomial p-value for `H1: p > 0.5`:
- `p = 0.598`

Interpretation:
- there is no statistical evidence here that `high` is better than `medium`
- there is also no evidence that `medium` dominates `high` under this looser timer regime

This is a competitive draw, not a superiority result.

## Descriptive Outcomes

Overall batch:
- games completed: `16 / 16`
- mean rounds: `8.0`
- mean elapsed time: `4307.55s`
- `15/16` games ended by direct `Territory Control 65%`
- `1/16` ended by `Max Rounds Reached - Territory Control`

Player win counts:
- `gpt-5.4-mini-medium-a`: `7`
- `gpt-5.4-mini-medium-b`: `1`
- `gpt-5.4-mini-high-a`: `5`
- `gpt-5.4-mini-high-b`: `3`

Side summary:

| Side | Wins | Mean Final Territories | Mean Turn Time (s) | Mean Strategic Score | Mean Fallback Count | Mean Placement Errors | Mean Attack Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `medium` | 8 | 9.60 | 505.71 | 4.775 | 0.03 | 0.09 | 0.09 |
| `high` | 8 | 11.41 | 1647.83 | 4.750 | 4.53 | 3.19 | 0.32 |

High-level read:
- the sides tied on wins
- `high` finished with slightly more territories on average
- `medium` was dramatically faster and cleaner
- strategic rubric scores were almost identical

## How The Games Played

The games were not mostly slow max-round slogs.

By winner side:
- `high` wins: `8`, all by direct `Territory Control 65%`
- `medium` wins: `8`, `7` by direct `Territory Control 65%`, `1` by max rounds

Representative decisive `high` wins:
- game `13`: `high-a` won `28 / 6 / 5 / 3`
- game `8`: `high-a` won `28 / 7 / 7 / 0`
- game `16`: `high-b` won `28 / 8 / 6 / 0`

Representative decisive `medium` wins:
- game `6`: `medium-a` won `28 / 7 / 6 / 1`
- game `15`: `medium-a` won `28 / 8 / 5 / 1`
- game `4`: `medium-a` won `28 / 9 / 5 / 0`

So this batch does not support a story where `high` merely survived longer without closing. It produced real, clean wins.

## What Changed Relative To The Earlier Constrained Experiment

This is the most important finding.

In the earlier constrained `120s` turn / `25s` placement experiment:
- `high` won only `1` game
- `high` had mean fallback count `18.88`
- `high` had mean placement errors `16.38`
- `high` had mean strategic score `4.26`

In this `300s` turn / `50s` placement recovery batch:
- `high` side won `8` games
- `high` mean fallback count dropped to `4.53`
- `high` mean placement errors dropped to `3.19`
- `high` mean strategic score rose to `4.75`

Conclusion:
- giving `high` more time clearly mattered
- the earlier collapse was heavily timer-driven

## Did `High` Show More Strategic Depth?

Yes, but only up to the point of competitiveness.

The observable traces show that `high` was no longer just stalling or failing to act. Its turn plans were coherent, continent-aware, and often multi-step.

Example `high` plan:
- [turn_summary_turn_7.json](../../../game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16/game__2026-04-29_05-11-10/turn_summary_turn_7.json)
- reinforce India and Afghanistan
- crack China for an Asia foothold
- preserve Australia shape while avoiding overextension

Example `medium` plan:
- [turn_summary_turn_8.json](../../../game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16/game__2026-04-28_20-27-35/turn_summary_turn_8.json)
- reinforce North Africa and Egypt
- push East Africa
- secure Africa while preserving European cover

These are both coherent and strategically legible.

That is why the correct conclusion is **not**:
- `high` became obviously smarter than `medium`

The better conclusion is:
- `high` became viable enough to compete with `medium`
- but it did not show a clearly different or superior strategic class of behavior

Evidence:
- strategic rubric scores were essentially tied: `4.75` vs `4.775`
- win counts were tied `8-8`
- no clean superiority signal emerged even with much more time

## Remaining Operational Gap

Even after recovery, `high` remained much slower and less reliable.

Phase-level fallback and timeout rates:

### `medium`
- initial placement fallback rate: `0.0%`
- troop placement fallback rate: `0.4%`
- pre-turn planning fallback rate: `0.0%`
- attack fallback rate: `0.0%`
- fortify fallback rate: `0.0%`

### `high`
- initial placement fallback rate: `2.0%`
- troop placement fallback rate: `28.0%`
- pre-turn planning fallback rate: `0.0%`
- attack fallback rate: `3.6%`
- fortify fallback rate: `4.5%`

Key point:
- planning was not the problem
- troop placement remained the dominant failure mode
- attack was much improved relative to the earlier constrained batch, but still slower and less stable than `medium`

Latency regimes were also very different.

`medium` p95 decision times:
- initial placement: `8.62s`
- troop placement: `19.97s`
- planning: `7.9s`
- attack: `15.19s`
- fortify: `15.71s`

`high` p95 decision times:
- initial placement: `41.35s`
- troop placement: `53.64s`
- planning: `29.63s`
- attack: `54.09s`
- fortify: `38.13s`

This means `high` was still operating in a much slower internal regime, even when it returned valid moves.

Concrete failure example:
- [0061_troop_placement.json](../../../game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16/llm_interactions/game__2026-04-28_14-57-49/gpt-5.4-mini-high-a/round_05/turn_0018/0061_troop_placement.json)
- fallback after `50.054s`
- error: `Wall-clock timeout exceeded 50.00 seconds.`

Concrete slow-but-successful example:
- [0029_attack.json](../../../game_results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16/llm_interactions/game__2026-04-28_14-57-49/gpt-5.4-mini-high-a/round_01/turn_0002/0029_attack.json)
- successful attack response
- still took `64.798s`

That second example matters because it shows the issue is not just parser failure. `high` is often spending a long time internally before producing a brief, normal move.

## What This Experiment Actually Shows

This batch answers one question clearly:
- if `high` is given much more time, it can recover from the catastrophic underperformance seen in the constrained live-turn experiment

But it does **not** answer a stronger claim:
- it does not show that `high` is better than `medium`

So the correct interpretation is:
- `high` was suppressed by the tighter clock
- but once that suppression is relaxed, the result is competitive parity, not dominance

That is a useful result because it narrows the question.

We now know the next question is not:
- “is high broken?”

It is:
- “where is high actually worth paying for?”

## Practical Conclusion

For normal synchronous live play, `medium` still looks like the better practical default.

Why:
- same win count as `high`
- far lower latency
- far fewer fallbacks
- far fewer placement errors
- equally good observable strategic trace

If the goal is a strong, efficient live-turn agent, `medium` is still the better choice.

## Caveat: Free-For-All Noise

This experiment also highlights the variance of four-player free-for-all Risk.

The two identical medium clones split:
- `medium-a`: `7` wins
- `medium-b`: `1` win

The two identical high clones split:
- `high-a`: `5` wins
- `high-b`: `3` wins

That tells us path dependence and board politics still create substantial noise. So an `8-8` side split should be interpreted as:
- no superiority signal
- not proof that both settings are exactly equal in all deeper senses

## Why The Hybrid Follow-Up Now Makes Sense

The bottleneck is now clear:
- `high` planning works
- `high` attack often works
- placement remains the biggest sink for time and fallbacks
- fortify is slower at `high` without clear evidence that it needs to be

So the next scientifically useful test is not simply “even more time.”

It is:
- `high` on planning and attack
- `medium` on placement, fortify, and card trade

That experiment isolates whether extra reasoning helps where it is most likely to matter strategically, without wasting budget on administrative phases.

## Bottom Line

The most defensible headline is:

- `high` recovered from collapse and became competitive when given much more time, but it still did not outperform `medium`.

Or more sharply:

- extra time was enough to make `high` viable, but not enough to make it superior.
