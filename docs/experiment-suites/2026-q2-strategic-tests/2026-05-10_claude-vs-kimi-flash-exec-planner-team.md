# Claude vs Kimi Flash-Exec Planner Team Duel

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Pooled series label: `claude_vs_kimi_flash_exec_planner_team_16_pooled`
- Raw pooled artifacts: `/shared-game-results/experiment_series/claude_vs_kimi_flash_exec_planner_team_16_pooled`
- Status: complete

## Question

After the pooled `32`-game four-way Flash-exec planner bakeoff showed only a weak descriptive Claude-over-Kimi edge, does a direct duplicate-team duel establish that `claude-opus-4-7` is a better planner than `kimi-k2.6` when both use the same `gemini-3-flash-preview` execution scaffold?

## Protocol

Lineup:
- `claude-opus-4-7-plan_gemini-3-flash-exec-a`
- `claude-opus-4-7-plan_gemini-3-flash-exec-b`
- `kimi-k2.6-plan_gemini-3-flash-exec-a`
- `kimi-k2.6-plan_gemini-3-flash-exec-b`

Shared condition:
- `4` clean shards of `4` games each
- `16` games total
- same frozen live strategic condition as the wider Flash-exec planner program
- planning timer `90s`
- execution turn timer `90s`
- placement timer `15s`
- seat rotation enabled within each shard

Why this design:
- the earlier four-way planner bakeoff wasted many games on Gemini and GPT wins that were irrelevant to the Claude-vs-Kimi question
- this duplicate-team duel makes every game informative for the pairwise comparison

## Primary Result: Wins

Wins are the primary endpoint.

Family wins over `16` games:
- `2x claude-opus-4-7-plan_gemini-3-flash-exec`: `9 / 16`
- `2x kimi-k2.6-plan_gemini-3-flash-exec`: `7 / 16`

Victory types:
- `16` direct `Territory Control 65%` wins
- `0` max-round wins

Interpretation:
- Claude has a small descriptive edge
- Kimi remains fully competitive on the primary endpoint

## Statistical Read

Exact family win test under equal team strength:
- one-sided `p ≈ 0.402`
- two-sided `p ≈ 0.804`

Bottom line:
- this duel does **not** establish a statistically significant Claude lead
- even after switching from a four-way field to a direct duplicate-team design, the observed edge is still too small

## Secondary Metrics

### Claude family
- wins: `9`
- mean final territories: `10.625`
- mean turn time seconds: `331.774`
- mean strategic score: `4.729`
- mean fallback count: `0.219`
- mean successful attacks per turn: `4.811`
- mean successful attacks per attacking turn: `5.132`
- mean attack-turn rate: `0.933`
- mean timed-out turns per game: `0.219`
- mean placement errors: `2.343`
- total successful attacks: `786`
- total failed attacks: `24`
- attack success rate: `97.04%`
- estimated total cost USD: `$5.602780`
- estimated cost per win USD: `$0.622531`

### Kimi family
- wins: `7`
- mean final territories: `10.375`
- mean turn time seconds: `702.763`
- mean strategic score: `4.379`
- mean fallback count: `2.562`
- mean successful attacks per turn: `5.335`
- mean successful attacks per attacking turn: `5.455`
- mean attack-turn rate: `0.978`
- mean timed-out turns per game: `0.157`
- mean placement errors: `2.531`
- total successful attacks: `846`
- total failed attacks: `20`
- attack success rate: `97.69%`
- estimated total cost USD: `$5.444586`
- estimated cost per win USD: `$0.777798`

## Copy Asymmetry

Per-player wins:
- `claude-opus-4-7-plan_gemini-3-flash-exec-a`: `2`
- `claude-opus-4-7-plan_gemini-3-flash-exec-b`: `7`
- `kimi-k2.6-plan_gemini-3-flash-exec-a`: `5`
- `kimi-k2.6-plan_gemini-3-flash-exec-b`: `2`

Interpretation:
- within-family variance is still large
- that is another reason to avoid turning a `9-7` split into a strong leaderboard claim

## Seat Check

Seat win counts:
- seat 1: `5`
- seat 2: `1`
- seat 3: `4`
- seat 4: `6`

Monte Carlo seat-effect check:
- `p ≈ 0.396`

So seat position does not explain the overall result.

## What The Result Means

This duel supports four narrower conclusions:

1. Claude planning is cleaner than Kimi planning under the shared Flash execution scaffold.
2. Claude planning is faster and has far lower fallback burden.
3. Kimi planning remains competitive on actual wins despite weaker secondary metrics.
4. The Flash-exec planner story remains the same as in the pooled four-way bakeoff:
   - planner differences are much smaller than the earlier full-stack provider gaps
   - Kimi planning is somewhat weaker descriptively, but not separated sharply enough on wins to justify a big claim

There is also a practical cost note:
- total spend is very similar between the two families
- Claude gets the better cost-per-win because it converted slightly more wins
- Kimi still posts strong attack volume and attack efficiency, but that does not translate into a decisive team win rate

## Bottom Line

The direct duplicate-team Claude-vs-Kimi duel is still a **near-parity result**.

Claude looks somewhat better descriptively:
- more wins
- much cleaner runtime
- higher strategic score

But the actual win gap is too small to prove that Claude planning is materially better than Kimi planning under the shared `gemini-3-flash-preview` execution scaffold.

For the broader article, the more important conclusion is not “Claude beats Kimi.” It is:
- once execution is standardized to a strong cheap scaffold, the remaining provider planning differences become much smaller and much harder to separate than the earlier full-stack provider differences
