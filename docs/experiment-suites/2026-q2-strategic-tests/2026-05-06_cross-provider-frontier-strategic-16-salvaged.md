# Cross-Provider Frontier Strategic 16: Salvaged Balanced Result

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Combined series label: `frontier_strategic_full_16_salvaged`
- Combined series artifacts: `/shared-game-results/experiment_series/frontier_strategic_full_16_salvaged`
- Source experiments:
  - `/shared-game-results/experiments/experiment__2026-05-04_21-00-11__frontier_strategic_full_16_retry_2`
  - `/shared-game-results/experiments/experiment__2026-05-05_19-02-22__frontier_strategic_topup_6`
- Status: complete

## Construction

This balanced `16`-game provider result was reconstructed from:

1. `frontier_strategic_full_16_retry_2`
   - kept games `1-6`
   - kept games `13-16`
   - dropped games `7-12` because Anthropic credits were exhausted during that window
2. `frontier_strategic_topup_6`
   - kept all `6` games

The top-up roster was ordered specifically to fill the missing seat counts from the clean retry-2 subset. The combined result restores perfect seat balance:

- `gpt-5.1`: `4` appearances in each seat
- `claude-opus-4-7`: `4` appearances in each seat
- `gemini-3.1-pro-preview`: `4` appearances in each seat
- `kimi-k2.6`: `4` appearances in each seat

## Primary Result: Wins

Wins are the primary endpoint.

Final win counts over the balanced `16` games:
- `gemini-3.1-pro-preview`: `10`
- `claude-opus-4-7`: `3`
- `gpt-5.1`: `2`
- `kimi-k2.6`: `1`

This is a clear Gemini lead.

Global win-inequality test:
- Monte Carlo chi-square test against the equal-strength `4 / 4 / 4 / 4` null
- observed win vector: `10 / 3 / 2 / 1`
- result: `p ≈ 0.0071`

Simple win-based calibration:
- if a specified player in a 4-player equal-strength field had only a `25%` chance to win each game, the probability of getting at least `10` wins in `16` games is about `0.00164`
- pairwise exact winner splits, conditioning only on wins by Gemini or the named opponent:
  - Gemini vs Claude: `10-3`, one-sided `p = 0.0461`, two-sided `p = 0.0923`
  - Gemini vs GPT-5.1: `10-2`, one-sided `p = 0.0193`, two-sided `p = 0.0386`
  - Gemini vs Kimi: `10-1`, one-sided `p = 0.00586`, two-sided `p = 0.0117`

These are still small-sample comparisons, but the balanced `16`-game result is strong enough to treat Gemini as the current leader of this provider field under the tested live condition.

## Structural Checks

Two structural questions mattered for this salvaged analysis.

### Seat effects

Winner seat counts:
- seat `1`: `4`
- seat `2`: `4`
- seat `3`: `2`
- seat `4`: `6`

Monte Carlo chi-square test against equal seat-win frequency:
- result: `p ≈ 0.609`

So the Gemini lead does **not** look like a seat-order artifact.

### Splice consistency

The salvaged series combines:
- a clean `10`-game retry-2 subset
- a clean `6`-game top-up

Gemini win rate by source:
- retry-2 clean subset: `6 / 10`
- top-up: `4 / 6`

Fisher exact comparison of those two source blocks:
- result: `p = 1.0`

So the top-up does not show evidence of behaving differently from the retained retry-2 subset.

## Secondary Metrics

Per-player aggregate metrics from `series_summary.json`:

### gemini-3.1-pro-preview
- wins: `10`
- mean final territories: `18.62`
- mean strategic score: `4.89`
- mean fallback count: `0.94`
- mean successful attacks per turn: `5.363`
- mean successful attacks per attacking turn: `5.423`
- mean timed-out turns per game: `0.88`

### claude-opus-4-7
- wins: `3`
- mean final territories: `9.06`
- mean strategic score: `4.86`
- mean fallback count: `0.12`
- mean successful attacks per turn: `4.421`
- mean successful attacks per attacking turn: `4.701`
- mean timed-out turns per game: `0.12`

### gpt-5.1
- wins: `2`
- mean final territories: `8.94`
- mean strategic score: `4.75`
- mean fallback count: `4.62`
- mean successful attacks per turn: `3.804`
- mean successful attacks per attacking turn: `3.96`
- mean timed-out turns per game: `3.56`

### kimi-k2.6
- wins: `1`
- mean final territories: `5.38`
- mean strategic score: `4.10`
- mean fallback count: `5.19`
- mean successful attacks per turn: `3.84`
- mean successful attacks per attacking turn: `4.468`
- mean timed-out turns per game: `0`

## Attack Conversion

Average successful attacks per game, recomputed from the saved turn summaries:
- `gemini-3.1-pro-preview`: `36.125`
- `claude-opus-4-7`: `29.25`
- `gpt-5.1`: `27.5`
- `kimi-k2.6`: `24.0`

Average failed attacks per game:
- `gemini-3.1-pro-preview`: `1.688`
- `gpt-5.1`: `4.438`
- `claude-opus-4-7`: `4.5`
- `kimi-k2.6`: `7.562`

This is the clearest mechanical explanation for the standings:
- Gemini captures more territories per game than the rest of the field
- Gemini also wastes the fewest attacks
- Claude is cleaner and more reliable than GPT-5.1, but still converts materially fewer attacks than Gemini
- Kimi remains the least efficient attacker in this field

Paired sign tests on successful attacks per game:
- Gemini > Claude in `13 / 16` games, one-sided `p = 0.0106`
- Gemini > GPT-5.1 in `13 / 16` games, one-sided `p = 0.0106`
- Gemini > Kimi in `14 / 16` games, one-sided `p = 0.00209`

This is stronger than the territory-share comparison and matches the visible game flow better. Gemini is not merely holding territory at the end; it is converting attack opportunities better throughout the batch.

Paired sign tests on final territories:
- Gemini > Claude in `11 / 16` games, one-sided `p = 0.105`
- Gemini > GPT-5.1 in `11 / 15` non-tied games, one-sided `p = 0.0592`
- Gemini > Kimi in `14 / 16` games, one-sided `p = 0.00209`

That split is informative:
- the win signal and attack-conversion signal are stronger than the territory-share signal against Claude and GPT-5.1
- this is one more reason wins remain the correct primary endpoint here

## Interpretation

The combined result points to three distinct profiles.

### Gemini: strongest practical live player

Gemini is the current winner of this provider field because it combines:
- the highest win count
- the highest territory conversion
- the highest successful-attack rate
- low fallback pressure

It is not merely surviving; it is turning turns into board control faster than the rest.

### Claude: clean but less explosive

Claude is the cleanest operational player in the field:
- almost no fallbacks
- almost no timeouts
- strong strategic scores

But it still trails Gemini on raw board conversion and total wins.

Operational reliability comparison:
- Claude had fewer fallbacks than GPT-5.1 in `14` non-tied paired games, one-sided `p ≈ 0.000061`
- Claude also had fewer fallbacks than Gemini in `8` of `9` non-tied paired games, one-sided `p ≈ 0.0195`

### GPT-5.1: strategically credible, operationally slower

GPT-5.1 is not collapsing strategically. Its strategic score remains solid. The issue is operational:
- higher fallback count
- many more timed-out turns than Gemini or Claude
- lower territory conversion than Gemini

Under this exact live `90 / 90 / 15` strategic setup, that operational drag is enough to leave it well behind Gemini.

Importantly, Claude does **not** beat GPT-5.1 on wins in a meaningful way here:
- Claude vs GPT-5.1 wins: `3-2`
- two-sided exact p-value: `1.0`

So the correct read is:
- Claude is much cleaner operationally
- but this batch is too small to claim Claude is actually stronger than GPT-5.1 on the primary endpoint

### Kimi: viable but weakest in this field

Kimi remains playable, but in this batch it was the weakest overall:
- fewest wins except for no-win outcomes
- lowest final territory share except where short-game variance helps
- highest failed-attack burden

## Bottom Line

For the current cross-provider strategic live-turn condition, this balanced salvaged `16`-game result supports:

1. `gemini-3.1-pro-preview` as the strongest current provider representative
2. `claude-opus-4-7` as the cleanest non-Gemini operational baseline
3. `gpt-5.1` as a credible but slower OpenAI representative under these timers
4. `kimi-k2.6` as the weakest of the four tested frontier candidates

This should now be treated as the current scored cross-provider strategic result.

The right next step is **not** another exploratory roster search. The right next step is a clean confirmatory replicate with the same lineup after the provider pause/resume handling is implemented, because that is the most direct test of whether Gemini's lead is stable.
