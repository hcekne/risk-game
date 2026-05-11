# Kimi Capability Anchoring vs Anthropic Sonnet 4 (20250514) Team Arena

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `kimi_anchor_anthropic_sonnet4_20250514_team_16`
- Raw artifacts: `/shared-game-results/experiments/experiment__2026-05-07_17-43-42__kimi_anchor_anthropic_sonnet4_20250514_team_16`
- Status: complete

## Question

In a duplicate-team `2x2` setup under the same frozen strategic live-turn condition, is `kimi-k2.6` clearly weaker than an older Anthropic Sonnet anchor, or does it remain broadly competitive once the comparison is made under a real operational live-game loop?

## Protocol

Lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `claude-sonnet-4-20250514-a`
- `claude-sonnet-4-20250514-b`

Shared condition:
- `16` games
- seat rotation enabled
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- same prompt pack, parser grammar, and rules used in the current provider program

Important configuration detail:
- the Anthropic Sonnet copies were run with `enable_thinking=true`
- the Kimi copies used the current split configuration:
  - execution thinking off
  - planning-only thinking on

So this is a valid live-deployment comparison under the repo’s current strategic harness, not a pure abstract-reasoning comparison.

## Primary Result: Wins

Wins are the primary endpoint.

Per-player wins:
- `claude-sonnet-4-20250514-b`: `5`
- `kimi-k2.6-b`: `5`
- `kimi-k2.6-a`: `4`
- `claude-sonnet-4-20250514-a`: `2`

Family-level win total:
- `kimi-k2.6` team: `9 / 16`
- `claude-sonnet-4-20250514` team: `7 / 16`

Exact binomial comparison under equal team strength:
- one-sided `p ≈ 0.402`
- two-sided `p ≈ 0.804`

Interpretation:
- Kimi has a small descriptive edge
- the win gap is not statistically significant
- the batch is fully compatible with near-parity on the primary endpoint

So this experiment does **not** prove that Kimi is stronger than this older Sonnet tier. It does show that Kimi is at least fully competitive in this live setting.

## Win Type Breakdown

Family-level wins by victory mode:

### Kimi team
- `Territory Control 65%`: `7`
- `Max Rounds Reached - Territory Control`: `2`

### Claude Sonnet 4 (20250514) team
- `Territory Control 65%`: `3`
- `Max Rounds Reached - Territory Control`: `4`

This is the most interesting pattern in the batch.

Kimi got more of its wins by actually reaching the game win condition.  
The Sonnet team got more of its wins by surviving to the round cap and finishing ahead on territory.

That suggests Kimi was the more direct closer, even though the overall family win split stayed narrow.

## Secondary Metrics

Per-player summary metrics from `experiment_summary.md`:

### claude-sonnet-4-20250514-a
- wins: `2`
- mean final territories: `9.00`
- mean turn time seconds: `1162.13`
- mean strategic score: `4.85`
- mean fallback count: `7.94`
- mean timed-out turns per game: `7.44`
- mean successful attacks per turn: `3.680`
- total successful attacks: `672`
- total failed attacks: `208`
- estimated total cost USD: `$19.237050`

### claude-sonnet-4-20250514-b
- wins: `5`
- mean final territories: `11.50`
- mean turn time seconds: `2227.20`
- mean strategic score: `4.83`
- mean fallback count: `7.31`
- mean timed-out turns per game: `7.19`
- mean successful attacks per turn: `3.809`
- total successful attacks: `653`
- total failed attacks: `192`
- estimated total cost USD: `$18.827988`

### kimi-k2.6-a
- wins: `4`
- mean final territories: `8.75`
- mean turn time seconds: `1096.13`
- mean strategic score: `4.16`
- mean fallback count: `6.50`
- mean timed-out turns per game: `0.00`
- mean successful attacks per turn: `3.669`
- total successful attacks: `586`
- total failed attacks: `256`
- estimated total cost USD: `$2.509819`

### kimi-k2.6-b
- wins: `5`
- mean final territories: `12.75`
- mean turn time seconds: `1194.70`
- mean strategic score: `4.19`
- mean fallback count: `7.38`
- mean timed-out turns per game: `0.12`
- mean successful attacks per turn: `4.412`
- total successful attacks: `711`
- total failed attacks: `249`
- estimated total cost USD: `$2.676556`

## Family-Level Aggregation

Because this is a duplicate-team arena, the most useful descriptive comparison is the family level.

### Claude Sonnet 4 (20250514) team
- wins: `7`
- mean final territories: `10.25`
- mean strategic score: `4.84`
- mean turn time seconds: `1694.67`
- mean fallback count: `7.625`
- mean successful attacks per turn: `3.745`
- mean successful attacks per attacking turn: `3.940`
- mean attack-turn rate: `0.941`
- mean timed-out turns per game: `7.315`
- total successful attacks: `1325`
- total failed attacks: `400`
- attack success rate: `76.8%`

### Kimi team
- wins: `9`
- mean final territories: `10.75`
- mean strategic score: `4.175`
- mean turn time seconds: `1145.42`
- mean fallback count: `6.94`
- mean successful attacks per turn: `4.041`
- mean successful attacks per attacking turn: `4.391`
- mean attack-turn rate: `0.913`
- mean timed-out turns per game: `0.06`
- total successful attacks: `1297`
- total failed attacks: `505`
- attack success rate: `72.0%`

## Cost

This batch is especially informative on cost because the Anthropic team was extremely expensive.

### Claude Sonnet 4 (20250514) team cost
- total estimated cost USD: `$38.065038`
- mean family cost per game: `$2.379065`
- estimated cost per win: `$5.437863`
- wins per USD: `0.184`
- successful attacks per USD: `34.8`

### Kimi team cost
- total estimated cost USD: `$5.186375`
- mean family cost per game: `$0.324148`
- estimated cost per win: `$0.576264`
- wins per USD: `1.735`
- successful attacks per USD: `250.1`

Interpretation:
- Kimi was dramatically cheaper
- Kimi also won slightly more games
- so on deployment economics, Kimi is far better in this batch

## What The Result Means

This experiment reveals a very sharp operational split.

The Sonnet team looked better on the repo’s strategic rubric:
- `4.84` vs `4.18`

But Kimi still won more games and reached the actual `65%` victory condition more often.

The best explanation is not that Kimi is the more elegant planner. It is that Kimi is more usable under this live harness:
- far fewer timed-out turns
- slightly more successful attacks per turn
- better real-finish conversion
- massively lower cost

So the result is another strong example of the repo’s core finding:
- apparent strategic sophistication and live strategic success are not the same thing
- operational reliability inside a bounded action loop matters a lot

## Bottom Line

The first Kimi-vs-Anthropic anchor batch does **not** show a clear strength gap between Kimi and this older Sonnet tier. If anything, it tilts slightly toward Kimi on actual game wins.

That matters because it sharpens the emerging Kimi picture:
- Kimi is roughly GPT-4.1-class here
- Kimi is somewhat below Gemini 2.5 Pro
- Kimi is at least competitive with, and operationally better deployed than, `claude-sonnet-4-20250514` under this harness
- Kimi is still clearly below the current Gemini 3.1 frontier result

So the current tiering story is now more precise:
- Kimi does **not** look frontier-class
- but it also does **not** look generally weak against older closed anchors
- it is strongest when the task rewards a usable, cheap, real-time agent rather than a slower model that looks more strategic on paper

The next disciplined step is one more clean replicate of this exact `2x kimi` vs `2x claude-sonnet-4-20250514` arena. If the pooled `32` games keep Kimi at or above parity, then the claim that Kimi is operationally stronger than this older Anthropic Sonnet tier becomes much more defensible.
