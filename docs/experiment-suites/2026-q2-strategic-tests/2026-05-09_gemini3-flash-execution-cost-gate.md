# Gemini 3 Flash Execution Cost Gate

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Pooled series label: `gemini3_flash_execution_cost_gate_15_pooled`
- Raw pooled artifacts: `/shared-game-results/experiment_series/gemini3_flash_execution_cost_gate_15_pooled`
- Source shards:
  - `/shared-game-results/experiments/experiment__2026-05-09_08-47-45__gemini3_flash_execution_cost_gate_shard_a_3`
  - `/shared-game-results/experiments/experiment__2026-05-09_08-47-56__gemini3_flash_execution_cost_gate_shard_b_3`
  - `/shared-game-results/experiments/experiment__2026-05-09_08-48-42__gemini3_flash_execution_cost_gate_shard_c_3`
  - `/shared-game-results/experiments/experiment__2026-05-09_08-48-52__gemini3_flash_execution_cost_gate_shard_d_3`
  - `/shared-game-results/experiments/experiment__2026-05-09_08-48-59__gemini3_flash_execution_cost_gate_shard_e_3`
- Status: complete

## Question

Can `gemini-3-flash-preview` replace `gemini-3.1-pro-preview` as the live execution scaffold without giving away too much strength, and if not, is a hybrid `gemini-3.1-pro-preview` planner on `gemini-3-flash-preview` execution the better practical default?

## Protocol

Lineup:
- `gemini-3.1-pro-full`
- `gemini-3-flash-full`
- `gemini-3.1-plan_gemini-3-flash-exec`

Shared condition:
- pooled from `5` clean shards of `3` games each
- `15` games total
- seat rotation enabled within each shard
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- same live prompt pack, parser grammar, and rules used in the broader strategic program

Important methodological note:
- this is a **cost gate**, not a final capability ranking
- the purpose is to choose a practical execution scaffold for later planner-only experiments

## Primary Result: Wins

Wins are the primary endpoint.

Pooled wins over `15` games:
- `gemini-3.1-plan_gemini-3-flash-exec`: `8 / 15`
- `gemini-3.1-pro-full`: `4 / 15`
- `gemini-3-flash-full`: `3 / 15`

Win types:
- `gemini-3.1-plan_gemini-3-flash-exec`: `8` direct `Territory Control 65%` wins
- `gemini-3.1-pro-full`: `3` direct `Territory Control 65%` wins, `1` max-round territory-lead win
- `gemini-3-flash-full`: `3` direct `Territory Control 65%` wins

Interpretation:
- the hybrid wins the most games
- it wins by actually closing games, not by surviving to the round cap
- pure Flash remains viable, but it does not match the hybrid on the primary endpoint

Statistical caution:
- this is still a small pooled batch for a three-way comparison
- the pooled winner split is not strong enough to claim a formally established winner on wins alone
- the point of the experiment is practical selection, not a publication-grade proof that one Gemini variant dominates the others

## Secondary Metrics

### gemini-3.1-plan_gemini-3-flash-exec
- wins: `8`
- mean final territories: `17.666`
- mean turn time seconds: `382.564`
- mean strategic score: `4.836`
- mean fallback count: `0.066`
- mean successful attacks per turn: `6.920`
- mean successful attacks per attacking turn: `6.987`
- mean attack-turn rate: `0.987`
- mean timed-out turns per game: `0.066`
- total successful attacks: `458`
- total failed attacks: `17`

### gemini-3.1-pro-full
- wins: `4`
- mean final territories: `13.534`
- mean turn time seconds: `432.726`
- mean strategic score: `4.862`
- mean fallback count: `0.802`
- mean successful attacks per turn: `4.869`
- mean successful attacks per attacking turn: `5.302`
- mean attack-turn rate: `0.967`
- mean timed-out turns per game: `0.802`
- total successful attacks: `391`
- total failed attacks: `20`

### gemini-3-flash-full
- wins: `3`
- mean final territories: `10.802`
- mean turn time seconds: `335.848`
- mean strategic score: `4.834`
- mean fallback count: `0.332`
- mean successful attacks per turn: `5.730`
- mean successful attacks per attacking turn: `5.766`
- mean attack-turn rate: `0.990`
- mean timed-out turns per game: `0.332`
- total successful attacks: `426`
- total failed attacks: `13`

## Cost

This experiment is useful because cost is a first-class part of the decision.

### gemini-3.1-pro-full
- estimated total cost USD: `$6.284960`
- mean cost per game USD: `$0.418997`
- estimated cost per win USD: `$1.571240`
- wins per USD: `0.636`
- successful attacks per USD: `62.212`

### gemini-3.1-plan_gemini-3-flash-exec
- estimated total cost USD: `$2.795970`
- mean cost per game USD: `$0.186398`
- estimated cost per win USD: `$0.349496`
- wins per USD: `2.861`
- successful attacks per USD: `163.807`

### gemini-3-flash-full
- estimated total cost USD: `$2.082246`
- mean cost per game USD: `$0.138817`
- estimated cost per win USD: `$0.694082`
- wins per USD: `1.441`
- successful attacks per USD: `204.587`

Interpretation:
- the hybrid is about `56%` cheaper than `gemini-3.1-pro-full`
- pure Flash is cheapest, but the hybrid converts cost into wins much better
- the hybrid is the strongest value point in this batch

## What The Result Means

This batch does **not** prove that the hybrid is the uniquely best Gemini configuration in a strict statistical sense.

It does support four narrower claims:

1. `gemini-3-flash-preview` is viable as a live execution model.
2. Pure Flash gives away enough on wins that it is not the best default benchmark scaffold.
3. `gemini-3.1-pro-preview` planning on `gemini-3-flash-preview` execution is much cheaper than `gemini-3.1-pro-preview` full-stack and performs better on the primary endpoint in this pooled batch.
4. For the next planner-only comparison, the right practical scaffold is:
   - `gemini-3.1-pro-preview` for planning
   - `gemini-3-flash-preview` for all non-planning phases

There is also a useful negative finding:
- pure `gemini-3-flash-preview` still got `3 / 15` wins
- so Flash is not collapsing operationally
- the main degradation appears to be in planning quality, not in basic execution viability

## Decision

The practical decision from this cost gate is:

- lock `gemini-3.1-plan_gemini-3-flash-exec` as the current cheap Gemini scaffold
- use that scaffold for the next cross-provider planner-only hybrid championship

That is a deployment decision, not yet a final paper-level theorem.

## Bottom Line

The Flash cost gate succeeded.

The repo now has a clear cheaper Gemini scaffold that remains strong enough to use as the default execution layer for the next stage:
- `gemini-3.1-pro-preview` planning
- `gemini-3-flash-preview` execution

That gives the project a much more affordable path into the next planner-only experiment without falling back to a weak baseline.
