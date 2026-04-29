# OpenAI Mini High-Strategic Hybrid Plan

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Planned label: `mini_high_strategic_hybrid_120s_16`
- Preset: `openai_mini_high_strategic_hybrid`
- Tracked roster file: `configs/experiments/openai_mini_high_strategic_hybrid.json`

## Research Question

Does `gpt-5.4-mini-high` help when it is reserved only for the strategically rich phases, while `medium` handles the faster administrative phases?

This is designed as a more normal-game-conditions follow-up to the completed recovery experiment, not as an immediate required run.

## Why This Experiment Exists

The completed `high` vs `medium` recovery test showed:
- `high` became competitive when given `300s` turns and `50s` placement
- but `high` still remained much slower and less reliable
- the dominant remaining failure mode was troop placement
- planning and many attack turns were coherent enough that they may still be where extra reasoning helps most

So this hybrid test isolates the likely value-bearing phases.

## Design

- Model family: `gpt-5.4-mini`
- Conditions:
  - `gpt-5.4-mini-medium-all-a`
  - `gpt-5.4-mini-medium-all-b`
  - `gpt-5.4-mini-high-strategic-a`
  - `gpt-5.4-mini-high-strategic-b`
- Games: `16`
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - turn timer `300s`
  - placement timer `25s`

Phase settings:

### `medium-all`
- placement: `medium`
- planning: `medium`
- attack: `medium`
- fortify: `medium`
- card trade: `medium`

### `high-strategic`
- placement: `medium`
- planning: `high`
- attack: `high`
- fortify: `medium`
- card trade: `medium`

## Hypotheses

Primary endpoint:
- game winner

Let:
- `X` = number of games won by the `high-strategic` side
- `n = 16`

Primary hypotheses:
- `H0: p <= 0.5`
- `H1: p > 0.5`

where `p` is the probability that a `high-strategic` player wins a game in this `2 vs 2` setup.

Primary test:
- exact one-sided binomial test with `X ~ Binomial(16, 0.5)` under `H0`

Planned rejection rule:
- reject `H0` if the high-strategic side wins at least `12/16` games

## What This Would Mean

If `high-strategic` wins clearly:
- the problem with all-phase `high` was mainly wasting time on administrative phases

If `high-strategic` still fails to beat `medium-all`:
- the practical strategic upside of `high` is probably small even when its biggest bottlenecks are removed

## Exact Commands

Preferred preset-based command:

```bash
make run-experiment ARGS="--label mini_high_strategic_hybrid_300s_16 --preset openai_mini_high_strategic_hybrid --num-games 16"
```

Equivalent explicit-roster command:

```bash
make run-experiment ARGS="--label mini_high_strategic_hybrid_300s_16 --agent-specs-file configs/experiments/openai_mini_high_strategic_hybrid.json --num-games 16 --turn-time-limit-seconds 300 --placement-time-limit-seconds 25"
```

Status checks:

```bash
make experiment-status
make experiment-summary
```
