# Kimi Capability Anchoring vs Gemini 2.5 Pro Team Arena

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `kimi_anchor_gemini25pro_team_16`
- Raw artifacts: `/shared-game-results/experiments/experiment__2026-05-07_15-35-19__kimi_anchor_gemini25pro_team_16`
- Status: complete

## Question

In a duplicate-team `2x2` setup under the same frozen strategic live-turn condition, is `kimi-k2.6` broadly competitive with an older strong Gemini tier, or does `gemini-2.5-pro` still hold a clear edge?

## Protocol

Lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `gemini-2.5-pro-a`
- `gemini-2.5-pro-b`

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
- `gemini-2.5-pro-b`: `6`
- `kimi-k2.6-a`: `5`
- `gemini-2.5-pro-a`: `3`
- `kimi-k2.6-b`: `2`

Family-level win total:
- `gemini-2.5-pro` team: `9 / 16`
- `kimi-k2.6` team: `7 / 16`

Exact binomial comparison under equal team strength:
- one-sided `p ≈ 0.038`
- two-sided `p ≈ 0.077`

Interpretation:
- Gemini 2.5 Pro has a modest descriptive edge
- under a directional pre-registered hypothesis, this supports `gemini-2.5-pro > kimi-k2.6`
- under a strict two-sided skeptic standard, the result is still short of conventional significance

So this is not a blowout. It is a narrow but coherent edge for Gemini 2.5 Pro.

## Win Type Breakdown

Family-level wins by victory mode:

### Gemini 2.5 Pro team
- `Territory Control 65%`: `6`
- `Max Rounds Reached - Territory Control`: `3`

### Kimi team
- `Territory Control 65%`: `5`
- `Max Rounds Reached - Territory Control`: `2`

This matters because the gap is not being driven only by one odd finish mode. Gemini leads both on direct territory-control wins and on max-round territory-lead finishes, but only narrowly in each.

## Secondary Metrics

Per-player summary metrics from `experiment_summary.md`:

### gemini-2.5-pro-a
- wins: `3`
- mean final territories: `11.31`
- mean turn time seconds: `1053.10`
- mean strategic score: `4.75`
- mean fallback count: `10.44`
- total reasoning tokens: `1,023,004`
- mean successful attacks per turn: `3.881`
- total successful attacks: `641`
- total failed attacks: `109`
- estimated total cost USD: `$3.368251`

### gemini-2.5-pro-b
- wins: `6`
- mean final territories: `13.69`
- mean turn time seconds: `1053.45`
- mean strategic score: `4.70`
- mean fallback count: `10.44`
- total reasoning tokens: `1,032,714`
- mean successful attacks per turn: `3.864`
- total successful attacks: `656`
- total failed attacks: `109`
- estimated total cost USD: `$3.393379`

### kimi-k2.6-a
- wins: `5`
- mean final territories: `12.06`
- mean turn time seconds: `1038.25`
- mean strategic score: `4.17`
- mean fallback count: `6.69`
- mean successful attacks per turn: `3.981`
- total successful attacks: `568`
- total failed attacks: `192`
- estimated total cost USD: `$2.251428`

### kimi-k2.6-b
- wins: `2`
- mean final territories: `4.94`
- mean turn time seconds: `950.36`
- mean strategic score: `4.22`
- mean fallback count: `5.88`
- mean successful attacks per turn: `3.631`
- total successful attacks: `489`
- total failed attacks: `167`
- estimated total cost USD: `$2.144540`

## Family-Level Aggregation

Because this is a duplicate-team arena, the most useful descriptive comparison is the family level.

### Gemini 2.5 Pro team
- wins: `9`
- mean final territories: `12.50`
- mean turn time seconds: `1053.28`
- mean strategic score: `4.725`
- mean fallback count: `10.44`
- mean successful attacks per turn: `3.872`
- mean successful attacks per attacking turn: `3.933`
- mean attack-turn rate: `0.986`
- mean timed-out turns per game: `6.375`
- total successful attacks: `1297`
- total failed attacks: `218`
- attack success rate: `85.6%`

### Kimi team
- wins: `7`
- mean final territories: `8.50`
- mean turn time seconds: `994.30`
- mean strategic score: `4.195`
- mean fallback count: `6.285`
- mean successful attacks per turn: `3.806`
- mean successful attacks per attacking turn: `4.042`
- mean attack-turn rate: `0.939`
- mean timed-out turns per game: `0.12`
- total successful attacks: `1057`
- total failed attacks: `359`
- attack success rate: `74.6%`

## Cost

This run used the new cost instrumentation, so the cost comparison is usable.

### Gemini 2.5 Pro team cost
- total estimated cost USD: `$6.761630`
- mean family cost per game: `$0.422602`
- estimated cost per win: `$0.751292`
- wins per USD: `1.331`
- successful attacks per USD: `191.8`

### Kimi team cost
- total estimated cost USD: `$4.395968`
- mean family cost per game: `$0.274748`
- estimated cost per win: `$0.627995`
- wins per USD: `1.592`
- successful attacks per USD: `240.4`

Interpretation:
- Gemini 2.5 Pro is stronger descriptively
- Kimi is cheaper
- Kimi still wins on cost-efficiency metrics

## What The Result Means

This experiment supports a tighter claim than the current-provider championship:

1. `gemini-2.5-pro` appears stronger than `kimi-k2.6` in this environment.
2. The gap is real enough to take seriously, but not yet large enough to call decisive from this first `16`-game batch alone.
3. Kimi remains economically attractive because it is materially cheaper on the new cost instrumentation.

There is also an important runtime nuance:
- Gemini 2.5 Pro uses much more reasoning and hits many more timed-out turns and fallbacks
- despite that runtime drag, it still edges Kimi on wins and on most strength-oriented descriptive metrics

That means this batch likely does **not** flatter Gemini 2.5 Pro. If anything, it probably understates Gemini's ceiling under a better-tuned runtime profile.

## Release-Lag Framing

This anchor result is useful because it gives a concrete reality check against vague benchmark claims about Kimi being only “a few months behind” stronger closed models.

Relevant public release dates:
- Google announced **Gemini 2.5 Pro Experimental** on **March 25, 2025**:
  - <https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/>
- Google announced **Gemini 2.5 Pro GA / stable** on **June 17, 2025**:
  - <https://blog.google/products/gemini/gemini-2-5-model-family-expands/>
- Moonshot announced **Kimi K2.6** on **April 21, 2026**:
  - <https://forum.moonshot.ai/t/meet-kimi-k2-6-advancing-open-source-coding/369>

So by release date:
- Kimi K2.6 arrives about **13 months after** Gemini 2.5 Pro's initial public release
- or about **10 months after** Gemini 2.5 Pro's GA/stable release

That is the stronger framing for this note:
- Kimi 2.6 is **newer**, not older, than Gemini 2.5 Pro
- yet in this live strategic environment it only reaches near-parity / modestly trails Gemini 2.5 Pro

This does **not** justify a literal “10-13 months behind” capability claim as a statistical theorem. Provider archives are sparse and release calendars are not directly comparable. But it does justify the public-facing interpretation that Kimi looks much closer to an older strong closed-model tier than to the current top provider frontier.

## Bottom Line

The first Kimi-vs-Gemini anchor batch places `kimi-k2.6` below `gemini-2.5-pro`, though not by a huge win margin.

That is the important public conclusion:
- Kimi does **not** look like the current provider frontier
- it does **not** even clearly surpass an older Gemini 2.5 Pro tier that predates it by roughly `10-13` months
- but it remains cost-competitive enough to matter for practical deployment conversations

Taken together with the Kimi-vs-GPT-4.1 anchor result, the current picture is:
- Kimi is roughly GPT-4.1-class here
- Gemini 2.5 Pro is a bit above it
- current Gemini frontier is well above it

The next disciplined step is one more clean replicate of this exact `2x kimi` vs `2x gemini-2.5-pro` arena. If the pooled `32` games preserve even a modest Gemini edge, then the tiering claim becomes much more defensible.
