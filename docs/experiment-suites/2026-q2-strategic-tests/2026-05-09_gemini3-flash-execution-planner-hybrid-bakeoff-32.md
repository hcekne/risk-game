# Gemini 3 Flash Execution Planner Hybrid Bakeoff 32

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Pooled series label: `gemini3_flash_execution_planner_hybrid_bakeoff_32_pooled`
- Raw pooled artifacts: `/shared-game-results/experiment_series/gemini3_flash_execution_planner_hybrid_bakeoff_32_pooled`
- Component pooled blocks:
  - first `16`: `/shared-game-results/experiment_series/gemini3_flash_execution_planner_hybrid_bakeoff_16_pooled`
  - replicate `16`: `/shared-game-results/experiment_series/gemini3_flash_execution_planner_hybrid_bakeoff_rep2_16_pooled`
- Status: complete

## Question

Once execution is fixed to the cheaper `gemini-3-flash-preview` scaffold, do the planning models from Gemini, OpenAI, Anthropic, and Moonshot separate clearly on wins, or do they collapse into roughly the same performance band?

## Protocol

Lineup:
- `gemini-3.1-plan_gemini-3-flash-exec`
- `gpt-5.5-plan_gemini-3-flash-exec`
- `claude-opus-4-7-plan_gemini-3-flash-exec`
- `kimi-k2.6-plan_gemini-3-flash-exec`

Shared condition:
- pooled from `8` clean shards of `4` games each
- `32` games total
- seat rotation enabled within each shard
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- same live prompt pack, parser grammar, and rules used in the broader strategic program

Important methodological note:
- this is a planner-isolation experiment
- the execution layer is deliberately held fixed at `gemini-3-flash-preview`
- the point is to estimate planning differences after most operational execution differences have been removed

## Primary Result: Wins

Wins are the primary endpoint.

Pooled wins over `32` games:
- `claude-opus-4-7-plan_gemini-3-flash-exec`: `10 / 32`
- `gemini-3.1-plan_gemini-3-flash-exec`: `8 / 32`
- `gpt-5.5-plan_gemini-3-flash-exec`: `8 / 32`
- `kimi-k2.6-plan_gemini-3-flash-exec`: `6 / 32`

Win rates:
- Claude planner: `31.25%`
- Gemini planner: `25.0%`
- GPT-5.5 planner: `25.0%`
- Kimi planner: `18.75%`

Victory types:
- `31` direct `Territory Control 65%` wins
- `1` `Max Rounds Reached - Territory Control` win

Interpretation:
- the field is much flatter than the earlier full-stack provider experiments
- Claude is the descriptive leader, but only narrowly
- Gemini and GPT-5.5 are tied on wins
- Kimi is last, but not dramatically separated on the primary endpoint

## Statistical Read

Winner-inequality omnibus test:
- Monte Carlo equal-winner test: `p ≈ 0.821`

This means the pooled `32`-game winner split is fully compatible with near-equality.

Selected exact pairwise win comparisons:

### Claude vs Gemini
- wins: `10` vs `8`
- one-sided `p ≈ 0.407`
- two-sided `p ≈ 0.815`

### Gemini vs GPT-5.5
- wins: `8` vs `8`
- one-sided `p ≈ 0.598`
- two-sided `p = 1.0`

### Claude vs GPT-5.5
- wins: `10` vs `8`
- one-sided `p ≈ 0.407`
- two-sided `p ≈ 0.815`

### Claude vs Kimi
- wins: `10` vs `6`
- one-sided `p ≈ 0.227`
- two-sided `p ≈ 0.454`

Bottom line:
- no planner lead is statistically established on wins
- if anything, the main result is that planner differences became much smaller after execution was standardized

## Secondary Metrics

### claude-opus-4-7-plan_gemini-3-flash-exec
- wins: `10`
- mean final territories: `12.562`
- mean turn time seconds: `419.538`
- mean strategic score: `4.820`
- mean fallback count: `0.531`
- mean successful attacks per turn: `5.943`
- mean successful attacks per attacking turn: `6.026`
- mean attack-turn rate: `0.982`
- mean timed-out turns per game: `0.531`
- mean placement errors: `2.438`
- total successful attacks: `1096`
- total failed attacks: `44`
- attack success rate: `96.14%`
- estimated total cost USD: `$7.044692`
- estimated cost per win USD: `$0.704469`

### gemini-3.1-plan_gemini-3-flash-exec
- wins: `8`
- mean final territories: `10.062`
- mean turn time seconds: `424.184`
- mean strategic score: `4.853`
- mean fallback count: `0.500`
- mean successful attacks per turn: `6.009`
- mean successful attacks per attacking turn: `6.071`
- mean attack-turn rate: `0.990`
- mean timed-out turns per game: `0.500`
- mean placement errors: `2.031`
- total successful attacks: `1044`
- total failed attacks: `33`
- attack success rate: `96.94%`
- estimated total cost USD: `$6.569050`
- estimated cost per win USD: `$0.821131`

### gpt-5.5-plan_gemini-3-flash-exec
- wins: `8`
- mean final territories: `9.344`
- mean turn time seconds: `427.518`
- mean strategic score: `4.755`
- mean fallback count: `0.344`
- mean successful attacks per turn: `5.586`
- mean successful attacks per attacking turn: `5.586`
- mean attack-turn rate: `1.000`
- mean timed-out turns per game: `0.250`
- mean placement errors: `2.875`
- total successful attacks: `893`
- total failed attacks: `34`
- attack success rate: `96.33%`
- estimated total cost USD: `$8.426483`
- estimated cost per win USD: `$1.053310`

### kimi-k2.6-plan_gemini-3-flash-exec
- wins: `6`
- mean final territories: `10.031`
- mean turn time seconds: `853.844`
- mean strategic score: `4.240`
- mean fallback count: `4.594`
- mean successful attacks per turn: `5.171`
- mean successful attacks per attacking turn: `5.206`
- mean attack-turn rate: `0.992`
- mean timed-out turns per game: `0.406`
- mean placement errors: `2.750`
- total successful attacks: `976`
- total failed attacks: `20`
- attack success rate: `97.99%`
- estimated total cost USD: `$5.358849`
- estimated cost per win USD: `$0.893142`

## What Changed Relative To The First 16

The first pooled `16` suggested a weak native-Gemini lead:
- Gemini `6`
- GPT-5.5 `4`
- Claude `3`
- Kimi `3`

The second pooled `16` flipped that:
- Claude `7`
- GPT-5.5 `4`
- Kimi `3`
- Gemini `2`

That reversal is the most important fact in the whole analysis.

Interpretation:
- the planner ranking is not stable at `16` games
- even at `32` games, the planner differences remain small enough that the winner order is still noisy

## Seat Check

Pooled seat win counts:
- seat 1: `13`
- seat 2: `8`
- seat 3: `3`
- seat 4: `8`

Monte Carlo seat-effect check:
- `p ≈ 0.113`

So seat imbalance is noticeable, but not clearly significant. It is not strong enough to rescue a claim that one planner clearly won and another was only dragged down by seat order.

## What The Result Means

This experiment does **not** support a strong leaderboard claim about planning quality.

It does support four narrower conclusions:

1. Once execution is standardized to `gemini-3-flash-preview`, planning-model differences are much smaller than the earlier full-stack provider differences.
2. Claude, Gemini, and GPT-5.5 all remain in roughly the same planning band on the primary endpoint.
3. `kimi-k2.6` remains the weakest planner on secondary metrics, especially strategic score and fallback burden, but the win gap is still not decisive.
4. The more important systems result is about decomposition:
   - fixing the execution scaffold removed a large part of the cross-provider spread
   - planner choice matters less than the earlier full-stack results suggested

There is also a practical cost result:
- GPT-5.5 planning is the most expensive option and does not buy a clear win advantage
- Claude planning is the descriptive win leader and has the best cost-per-win in this pooled `32`
- native Gemini planning remains competitive and simpler to operate

## Bottom Line

The pooled `32`-game Flash-exec planner bakeoff is **inconclusive as a planner leaderboard**.

That is not a failed experiment. It is an informative one.

The main lesson is:
- after the system is decomposed and execution is fixed to a cheaper Gemini scaffold, the remaining provider differences in planning are much smaller than the full-stack tournament suggested

For the article, that is a stronger systems-design result than a weak “Claude won” or “Gemini won” headline would have been.

If the next question is specifically whether Claude planning is better than Kimi planning under the same Flash execution scaffold, the right next move is **not** another 4-way bakeoff. It is a direct duplicate-team `2x Claude` vs `2x Kimi` duel.
