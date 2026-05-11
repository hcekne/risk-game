# Cross-Provider Frontier Strategic Replicate 2

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `frontier_strategic_replicate_2_16`
- Raw artifacts: `/shared-game-results/experiments/experiment__2026-05-06_11-13-05__frontier_strategic_replicate_2_16`
- Status: complete

## Protocol

This run is a direct replicate of the current frozen strategic provider lineup:

- OpenAI: `gpt-5.1` execution plus `gpt-5.5` planning
- Anthropic: `claude-opus-4-7`
- Gemini: `gemini-3.1-pro-preview`
- Moonshot: `kimi-k2.6`

Shared condition:
- seat rotation enabled
- `16` games
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- same prompt pack, parser grammar, and game rules as the prior balanced provider result

## Primary Result: Wins

Wins are the primary endpoint.

Final win counts:
- `gemini-3.1-pro-preview`: `10`
- `gpt-5.1`: `4`
- `claude-opus-4-7`: `1`
- `kimi-k2.6`: `1`

This is a direct replication of the main headline from the earlier balanced provider result: Gemini again won `10 / 16` games.

Global win-inequality test:
- Monte Carlo chi-square test against the equal-strength `4 / 4 / 4 / 4` null
- observed win vector: `10 / 4 / 1 / 1`
- result: `p ≈ 0.00370`

Simple win calibration:
- if a specified player in a 4-player equal-strength field had only a `25%` chance to win each game, the probability of getting at least `10` wins in `16` games is about `0.00164`

Pairwise exact winner splits, conditioning only on wins by Gemini or the named opponent:
- Gemini vs GPT-5.1: `10-4`, one-sided `p ≈ 0.0898`, two-sided `p ≈ 0.1796`
- Gemini vs Claude: `10-1`, one-sided `p = 0.00586`, two-sided `p = 0.0117`
- Gemini vs Kimi: `10-1`, one-sided `p = 0.00586`, two-sided `p = 0.0117`

Interpretation:
- the replicate alone clearly re-establishes Gemini ahead of Claude and Kimi
- the replicate alone does not fully separate Gemini from GPT-5.1 on wins
- that is the correct place to pool with the previous balanced `16` rather than overstate a single-batch result

## Seat Check

Winner seat counts:
- seat `1`: `1`
- seat `2`: `4`
- seat `3`: `5`
- seat `4`: `6`

Monte Carlo chi-square test against equal seat-win frequency:
- result: `p ≈ 0.396`

So this replicate does not show a detectable seat-order artifact.

## Secondary Metrics

Per-player aggregate metrics from `experiment_summary.json`:

### gemini-3.1-pro-preview
- wins: `10`
- mean final territories: `19.06`
- mean strategic score: `4.86`
- mean turn time seconds: `768.21`
- mean fallback count: `3.56`
- mean successful attacks per turn: `4.875`
- mean successful attacks per attacking turn: `4.948`
- mean attack-turn rate: `0.983`
- mean timed-out turns per game: `2.50`

### gpt-5.1
- wins: `4`
- mean final territories: `12.50`
- mean strategic score: `4.72`
- mean turn time seconds: `851.80`
- mean fallback count: `8.31`
- mean successful attacks per turn: `4.033`
- mean successful attacks per attacking turn: `4.128`
- mean attack-turn rate: `0.974`
- mean timed-out turns per game: `5.62`

### claude-opus-4-7
- wins: `1`
- mean final territories: `6.06`
- mean strategic score: `4.77`
- mean turn time seconds: `299.24`
- mean fallback count: `0.94`
- mean successful attacks per turn: `3.642`
- mean successful attacks per attacking turn: `4.08`
- mean attack-turn rate: `0.885`
- mean timed-out turns per game: `0.06`

### kimi-k2.6
- wins: `1`
- mean final territories: `4.38`
- mean strategic score: `4.13`
- mean turn time seconds: `978.12`
- mean fallback count: `6.50`
- mean successful attacks per turn: `3.791`
- mean successful attacks per attacking turn: `4.392`
- mean attack-turn rate: `0.885`
- mean timed-out turns per game: `0.31`

## Interpretation

The replicate reinforces three conclusions.

1. Gemini remains the strongest player in this provider field under the frozen `90 / 90 / 15` strategic condition.
2. Kimi remains last in the field.
3. The unstable part of the ordering is the second-place contest between GPT-5.1 and Claude, not the identity of the winner.

Operationally, the field still separates into three profiles:
- Gemini wins because it combines the highest win rate with the strongest attack conversion and acceptable runtime stability.
- Claude remains the cleanest runtime, but that cleanliness does not convert into enough wins.
- GPT-5.1 remains strategically credible but slower and more fallback-prone than Gemini.

## Bottom Line

This replicate is a successful confirmation of the earlier Gemini-led provider result.

It should be reported separately as the confirmatory batch, then pooled with the earlier balanced `16`-game provider set to produce the current `32`-game cross-provider estimate.

## Cost Note

This run started before token-usage and pricing aggregation landed in the runtime summaries. It should therefore be treated as a pre-cost-instrumentation batch for reporting purposes.
