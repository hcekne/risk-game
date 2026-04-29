# OpenAI Mini High-vs-Medium Recovery Plan

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Planned label: `mini_medium_vs_high_300s_16`
- Preset: `openai_mini_medium_vs_high`
- Tracked roster file: `configs/experiments/openai_mini_medium_vs_high.json`

## Research Question

Does `gpt-5.4-mini-high` recover against `gpt-5.4-mini-medium` when the live-turn budget is relaxed enough that repeated in-turn decisions are less likely to time out?

This is not a general “which mode is smarter in all circumstances?” test.

It is a more focused question:
- if `high` is given a more permissive synchronous clock, does it win more often than `medium`?

## Why This Follow-Up Exists

The earlier `openai_mini_reasoning` batch showed:
- `medium` was the strongest usable setting under `120s` turns and `25s` placement
- `high` was badly hurt by repeated in-turn timeouts and fallbacks
- the shared turn budget mattered because one slow attack decision consumed time needed for later attacks and fortification in the same turn

So this follow-up is intentionally framed as a recovery test under a looser live clock.

## Design

- Model family: `gpt-5.4-mini`
- Conditions:
  - `gpt-5.4-mini-medium-a`
  - `gpt-5.4-mini-medium-b`
  - `gpt-5.4-mini-high-a`
  - `gpt-5.4-mini-high-b`
- Games: `16`
- Seats: `4-player`, seat-rotated
- Seat balance goal: each profile should occupy each seat equally often across the batch
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - turn timer `300s`
  - placement timer `50s`

## Primary Endpoint

- game winner

For each game:
- success for the `high` side = winner is `gpt-5.4-mini-high-a` or `gpt-5.4-mini-high-b`
- success for the `medium` side = winner is `gpt-5.4-mini-medium-a` or `gpt-5.4-mini-medium-b`

Let:
- `X = number of games won by the high side`
- `n = 16`

## Hypotheses

Primary test:
- `H0: p <= 0.5`
- `H1: p > 0.5`

where:
- `p` = probability that a `high` player wins a game in this `2 high vs 2 medium` setup

Interpretation:
- under equal strength, the `high` side should win about half the games because it holds half the seats
- if `high` is genuinely better under the larger timer budget, it should win more than half the games

## Statistical Test

Use an exact one-sided binomial test.

Under `H0`:
- `X ~ Binomial(n=16, p=0.5)`

Exact probability mass:

```text
P(X = k) = C(16, k) * (0.5)^16
```

One-sided p-value for observed `x_obs` high-side wins:

```text
P(X >= x_obs) = sum from k=x_obs to 16 of C(16, k) * (0.5)^16
```

## Rejection Rule

At one-sided `alpha = 0.05`, reject `H0` if the high side wins at least `12` of `16` games.

Threshold details:
- `11/16` high wins: `p ≈ 0.105`
- `12/16` high wins: `p ≈ 0.038`
- `13/16` high wins: `p ≈ 0.011`
- `14/16` high wins: `p ≈ 0.002`

So the practical read is:
- `12-4` is the minimum statistically significant superiority result for `high`
- `13-3` or better is a cleaner headline result

## Secondary Diagnostics

Even though wins are the primary endpoint, still inspect:
- fallback counts
- placement-error counts
- average turn time
- attack-timeout frequency

Reason:
- if `high` still loses badly, these diagnostics will show whether it is still mostly a timing/operational failure or a deeper strategic failure

## Exact Commands

Preferred preset-based command:

```bash
make run-experiment ARGS="--label mini_medium_vs_high_300s_16 --preset openai_mini_medium_vs_high --num-games 16"
```

Equivalent explicit-roster command:

```bash
make run-experiment ARGS="--label mini_medium_vs_high_300s_16 --agent-specs-file configs/experiments/openai_mini_medium_vs_high.json --num-games 16 --turn-time-limit-seconds 300 --placement-time-limit-seconds 50"
```

Status checks:

```bash
make experiment-status
make experiment-summary
```

## Interpretation Targets

Three outcomes are especially informative:

1. `High` wins `12+ / 16`
- supports the claim that `high` was mainly being suppressed by the tighter timer regime

2. `High` improves operationally but still does not win `12 / 16`
- suggests that more time helps, but not enough to make `high` superior to `medium`

3. `High` still has heavy fallback/timeout behavior even at `300s / 50s`
- suggests `high` may simply be a poor fit for synchronous live play in this environment
