# Cross-Provider Frontier Strategic 32: Pooled Result

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Combined series label: `frontier_strategic_provider_32_pooled`
- Combined series artifacts: `/shared-game-results/experiment_series/frontier_strategic_provider_32_pooled`
- Source series:
  - `/shared-game-results/experiment_series/frontier_strategic_full_16_salvaged`
  - `/shared-game-results/experiments/experiment__2026-05-06_11-13-05__frontier_strategic_replicate_2_16`
- Status: complete

## Why Pooling Is Valid Here

These `32` games were run under the same effective scored condition:

- same four-provider lineup
- same game mechanics and victory rule
- same `90s` planning timer
- same `90s` execution turn timer
- same `15s` placement timer
- same prompt pack and parser grammar
- same seat-rotation policy

The earlier `16`-game block was a balanced salvaged series, but it was already cleaned, top-upped, and restored to perfect seat balance before pooling. The later `16`-game block was a clean direct replicate.

Standard reporting practice here is:
1. report each replicate on its own
2. confirm that the headline direction matches
3. then pool the runs for the best current effect estimate

That is what this note does.

## Primary Result: Wins

Wins are the primary endpoint.

Pooled win counts over `32` games:
- `gemini-3.1-pro-preview`: `20`
- `gpt-5.1`: `6`
- `claude-opus-4-7`: `4`
- `kimi-k2.6`: `2`

Win rates:
- Gemini: `62.5%`
- GPT-5.1: `18.75%`
- Claude: `12.5%`
- Kimi: `6.25%`

This is now strong enough to state plainly:

Under the current frozen strategic live-turn setup, Gemini is the best model in this tested provider field.

Global win-inequality test:
- Monte Carlo chi-square test against the equal-strength `8 / 8 / 8 / 8` null
- observed win vector: `20 / 6 / 4 / 2`
- result: `p ≈ 0.000015`

Simple win calibration:
- if a specified player in a 4-player equal-strength field had only a `25%` chance to win each game, the probability of getting at least `20` wins in `32` games is about `7.98e-06`

Pairwise exact winner splits, conditioning only on wins by Gemini or the named opponent:
- Gemini vs GPT-5.1: `20-6`, one-sided `p ≈ 0.00468`, two-sided `p ≈ 0.00936`
- Gemini vs Claude: `20-4`, one-sided `p ≈ 0.000772`, two-sided `p ≈ 0.00154`
- Gemini vs Kimi: `20-2`, one-sided `p ≈ 0.0000606`, two-sided `p ≈ 0.000121`

Interpretation:
- pooling the two balanced `16`-game blocks resolves the main provider question cleanly
- Gemini is now separated from all three rivals on the primary win endpoint

## Replicate Structure

The pooled result does not hide the replicate structure.

Source block A, balanced salvaged `16`:
- Gemini `10`
- Claude `3`
- GPT-5.1 `2`
- Kimi `1`

Source block B, clean direct replicate `16`:
- Gemini `10`
- GPT-5.1 `4`
- Claude `1`
- Kimi `1`

What replicated cleanly:
- Gemini stayed first
- Kimi stayed last
- Gemini posted the same `10 / 16` win count in both halves

What remained noisy:
- GPT-5.1 vs Claude for second place

That is exactly the pattern expected from a real headline effect plus a weaker unresolved secondary ordering.

## Seat Check

Winner seat counts across the pooled `32`:
- seat `1`: `5`
- seat `2`: `8`
- seat `3`: `7`
- seat `4`: `12`

Monte Carlo chi-square test against equal seat-win frequency:
- result: `p ≈ 0.392`

So the pooled Gemini lead is not plausibly a seat-order artifact.

## Secondary Metrics

Per-player aggregate metrics from `series_summary.json`:

### gemini-3.1-pro-preview
- wins: `20`
- mean final territories: `18.84`
- mean strategic score: `4.87`
- mean turn time seconds: `645.63`
- mean fallback count: `2.25`
- mean successful attacks per turn: `5.119`
- mean successful attacks per attacking turn: `5.185`
- mean attack-turn rate: `0.985`
- mean timed-out turns per game: `1.69`
- total successful attacks: `1253`
- total failed attacks: `52`

### gpt-5.1
- wins: `6`
- mean final territories: `10.72`
- mean strategic score: `4.73`
- mean turn time seconds: `724.45`
- mean fallback count: `6.47`
- mean successful attacks per turn: `3.918`
- mean successful attacks per attacking turn: `4.044`
- mean attack-turn rate: `0.964`
- mean timed-out turns per game: `4.59`
- total successful attacks: `984`
- total failed attacks: `188`

### claude-opus-4-7
- wins: `4`
- mean final territories: `7.56`
- mean strategic score: `4.82`
- mean turn time seconds: `284.47`
- mean fallback count: `0.53`
- mean successful attacks per turn: `4.032`
- mean successful attacks per attacking turn: `4.391`
- mean attack-turn rate: `0.91`
- mean timed-out turns per game: `0.09`
- total successful attacks: `934`
- total failed attacks: `153`

### kimi-k2.6
- wins: `2`
- mean final territories: `4.88`
- mean strategic score: `4.12`
- mean turn time seconds: `873.28`
- mean fallback count: `5.84`
- mean successful attacks per turn: `3.815`
- mean successful attacks per attacking turn: `4.43`
- mean attack-turn rate: `0.876`
- mean timed-out turns per game: `0.16`
- total successful attacks: `865`
- total failed attacks: `309`

## Why Gemini Wins

The pooled mechanism is consistent across both source blocks.

Gemini is not winning on one lucky axis. It leads on all of the important live-game conversion dimensions:
- highest win count
- highest mean final territories
- highest mean strategic score in the provider field
- highest successful attacks per turn
- highest successful attacks per attacking turn
- lowest failed-attack total
- acceptable, not perfect, runtime stability

The others each have a visible limitation:

### Claude
- strongest runtime cleanliness
- near-zero timeout burden
- low fallback pressure
- but not enough board conversion to challenge Gemini on wins

### GPT-5.1
- credible strategic scores
- reasonable attack rate
- but much heavier timeout and fallback drag than Gemini

### Kimi
- viable enough to play the format
- but clearly below the frontier closed models in both wins and attack efficiency

## Interpretation

At this point, the best way to view the provider data is:

1. the latest `16`-game run is the confirmatory replicate
2. the pooled `32` is the best current estimate of the actual provider ordering under this setup
3. the Gemini lead should now be treated as a real result rather than a one-off tournament surprise

This does not imply Gemini is the best model in every possible benchmark or deployment condition. It does imply that, under this exact frozen live-turn Risk condition, Gemini is the strongest tested provider representative.

## Cost Note

The pooled `32` series combines runs that predate token-usage and pricing aggregation. Cost fields in `series_summary.json` are therefore zero or null and should not be interpreted. Cost-efficiency comparisons need to come from future batches started after the pricing instrumentation landed.
