# Kimi Capability Anchoring vs OpenAI GPT-4.1 Team Arena

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `kimi_anchor_openai_gpt41_team_16`
- Raw artifacts: `/shared-game-results/experiments/experiment__2026-05-07_15-34-43__kimi_anchor_openai_gpt41_team_16`
- Status: complete

## Question

In a duplicate-team `2x2` setup under the same frozen strategic live-turn condition, is `kimi-k2.6` clearly weaker than `gpt-4.1`, or does it look broadly competitive with that older OpenAI anchor tier?

## Protocol

Lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `gpt-4.1-a`
- `gpt-4.1-b`

Shared condition:
- `16` games
- seat rotation enabled
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- same prompt pack, parser grammar, and rules used in the current provider program

## Primary Result: Wins

Wins are the primary endpoint.

Per-player wins:
- `gpt-4.1-b`: `5`
- `gpt-4.1-a`: `4`
- `kimi-k2.6-a`: `4`
- `kimi-k2.6-b`: `3`

Family-level win total:
- `gpt-4.1` team: `9 / 16`
- `kimi-k2.6` team: `7 / 16`

Exact binomial comparison under equal team strength:
- one-sided `p ≈ 0.402`
- two-sided `p ≈ 0.804`

Interpretation:
- GPT-4.1 has a small descriptive edge
- the win gap is not remotely significant
- this batch is consistent with near-parity on the primary endpoint

That is already a meaningful result. Kimi does **not** look obviously below GPT-4.1 in this environment.

## Secondary Metrics

Per-player summary metrics from `experiment_summary.md`:

### gpt-4.1-a
- wins: `4`
- mean final territories: `11.31`
- mean turn time seconds: `197.52`
- mean strategic score: `4.75`
- mean fallback count: `0`
- mean successful attacks per turn: `4.386`
- total successful attacks: `553`
- total failed attacks: `276`
- estimated total cost USD: `$4.325386`

### gpt-4.1-b
- wins: `5`
- mean final territories: `11.69`
- mean turn time seconds: `169.76`
- mean strategic score: `4.68`
- mean fallback count: `0`
- mean successful attacks per turn: `4.621`
- total successful attacks: `542`
- total failed attacks: `251`
- estimated total cost USD: `$4.162456`

### kimi-k2.6-a
- wins: `4`
- mean final territories: `10.00`
- mean turn time seconds: `873.74`
- mean strategic score: `4.21`
- mean fallback count: `5.31`
- mean successful attacks per turn: `4.232`
- total successful attacks: `511`
- total failed attacks: `172`
- estimated total cost USD: `$2.120897`

### kimi-k2.6-b
- wins: `3`
- mean final territories: `9.00`
- mean turn time seconds: `909.69`
- mean strategic score: `4.13`
- mean fallback count: `5.94`
- mean successful attacks per turn: `3.849`
- total successful attacks: `522`
- total failed attacks: `151`
- estimated total cost USD: `$2.007006`

## Family-Level Aggregation

Because this is a duplicate-team arena, the most useful descriptive comparison is the family level.

### GPT-4.1 team
- wins: `9`
- mean final territories: `11.50`
- mean turn time seconds: `183.64`
- mean strategic score: `4.715`
- mean fallback count: `0.0`
- mean successful attacks per turn: `4.504`
- mean successful attacks per attacking turn: `4.689`
- mean attack-turn rate: `0.957`
- mean timed-out turns per game: `0.0`
- total successful attacks: `1095`
- total failed attacks: `527`
- attack success rate: `67.5%`

### Kimi team
- wins: `7`
- mean final territories: `9.50`
- mean turn time seconds: `891.72`
- mean strategic score: `4.17`
- mean fallback count: `5.625`
- mean successful attacks per turn: `4.040`
- mean successful attacks per attacking turn: `4.548`
- mean attack-turn rate: `0.884`
- mean timed-out turns per game: `0.06`
- total successful attacks: `1033`
- total failed attacks: `323`
- attack success rate: `76.2%`

## Cost

This batch is the first Kimi anchor result with cost instrumentation enabled, so the cost comparisons are usable.

### GPT-4.1 team cost
- total estimated cost USD: `$8.487842`
- mean family cost per game: `$0.530490`
- estimated cost per win: `$0.943094`
- wins per USD: `1.060`
- successful attacks per USD: `129.0`

### Kimi team cost
- total estimated cost USD: `$4.127903`
- mean family cost per game: `$0.257994`
- estimated cost per win: `$0.589700`
- wins per USD: `1.696`
- successful attacks per USD: `250.2`

Interpretation:
- Kimi is much cheaper than GPT-4.1 in this setup
- GPT-4.1 wins slightly more games
- but Kimi is clearly better on cost-efficiency metrics

## What The Result Means

This experiment does **not** prove that Kimi is stronger than GPT-4.1.

It does support three narrower claims:

1. `kimi-k2.6` is competitive with `gpt-4.1` on wins in this live strategic Risk condition.
2. `gpt-4.1` is operationally cleaner:
   - zero fallbacks
   - much lower turn time
3. `kimi-k2.6` is materially better on cost efficiency:
   - roughly half the total estimated cost
   - lower estimated cost per win
   - much higher successful-attacks-per-dollar

There is also an interesting tactical split:
- GPT-4.1 attacks more aggressively and converts a slightly larger absolute number of attacks
- Kimi wastes fewer attacks and posts a better raw attack success rate

So the qualitative picture is:
- GPT-4.1 is cleaner and somewhat more forceful
- Kimi is slower and noisier, but not strategically outclassed
- Kimi is much cheaper

## Bottom Line

The first Kimi-vs-OpenAI anchor batch places `kimi-k2.6` roughly in the `gpt-4.1` band for this environment rather than near the current provider frontier.

That is already a strong public-facing conclusion:
- Kimi does **not** look like current Gemini or the current best provider representative
- but it also does **not** look far below a still-strong older closed-model tier
- on cost, it may be the better practical choice for some live strategic workloads

The next disciplined step is one more clean replicate of this exact `2x kimi` vs `2x gpt-4.1` arena. If the pooled `32` games stay near parity, then the “Kimi is approximately GPT-4.1-tier here” claim becomes much more defensible.
