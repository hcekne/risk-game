# OpenAI Generation Ladder Strategic 32

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Combined experiment label: `openai_generation_ladder_541_strategic_32`
- Raw local artifacts:
  - `/shared-game-results/experiments/experiment__2026-05-02_09-00-55__openai_generation_ladder_541_strategic_16`
  - `/shared-game-results/experiments/experiment__2026-05-03_07-17-54__openai_generation_ladder_541_strategic_16_rep2`
- Core files in each artifact folder:
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`
  - per-game `turn_summary_turn_*.json`

## Research Question

Under the repo's strategic live-turn condition, which OpenAI generation is the strongest practical Risk agent once planning gets its own isolated budget and execution still has to finish inside a strict synchronous clock?

More concretely:
- does the newest model generation actually convert into better live play?
- is `gpt-5.1` really stronger than `gpt-5.2`, `gpt-5.4`, and `gpt-4.1` here, or was the first `16`-game run just noise?
- if one model wins, is it because it plans better, executes faster, or avoids timeouts better?

Important historical framing:
- after the first `16`-game replicate, the main unresolved question was not whether `gpt-5.1` was leading the field in raw wins
- the unresolved question was whether the apparent `gpt-5.1 > gpt-5.2` edge would hold up in a second replicate
- the second `16` games were therefore not just a generic rerun; they were a targeted follow-up on that specific comparison

## Design

This note combines two completed `16`-game replicates into one `32`-game blocked analysis because both runs used the same roster, same timers, same rules, and same seat-rotation policy.

- Conditions:
  - `gpt-5.4`
  - `gpt-5.2`
  - `gpt-5.1`
  - `gpt-4.1`
- Games: `32` total
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - isolated pre-turn planning timer `90s`
  - shared execution turn timer `90s`
  - placement timer `15s`
  - `gpt-5.4`, `gpt-5.2`, `gpt-5.1` phase reasoning:
    - placement `medium`
    - planning `high`
    - attack `medium`
    - fortify `medium`
    - card trade `low`
  - `gpt-4.1`:
    - no reasoning-effort controls in this repo path

Important protocol note:
- the primary endpoint is wins under the configured `65%` territory-control victory rule
- final territory totals are secondary diagnostics that help explain margins and execution quality
- the main inferential tests therefore use winner-based tests first and territory totals second
- because the second replicate was launched to resolve the `gpt-5.1` lead signaled by the first replicate, this note reports both:
  - the very strict all-pairs family across all `6` unordered pairwise comparisons
  - the narrower `gpt-5.1`-vs-rest family that matches the actual follow-up question

## Hypotheses

Primary blocked comparison:
- `H0`: within each game block, the four models are exchangeable on winner outcome
- `H1`: at least one model differs

Main post-hoc question:
- if the omnibus test rejects `H0`, does `gpt-5.1` beat the other models on wins after Holm correction?

Focused follow-up question:
- given that the first `16` games already suggested `gpt-5.1` was the likely leader, does the combined `32`-game evidence support `gpt-5.1 > gpt-5.2` when the comparison family is limited to the actual follow-up target set: `gpt-5.1` versus the other candidates?

Supporting descriptive question:
- if `gpt-5.1` wins, is it because it is visibly more strategic, or because it converts turns into successful attacks and territory more efficiently under the live clock?

## Core Result

`gpt-5.1` was the clear winner in the combined `32`-game experiment.

Win counts:
- `gpt-5.1`: `18 / 32`
- `gpt-5.2`: `7 / 32`
- `gpt-4.1`: `4 / 32`
- `gpt-5.4`: `3 / 32`

Primary win test:
- winner-label permutation omnibus on the `32` game outcomes: `p = 0.000485`

Holm-corrected pairwise win tests:
- `gpt-5.1 > gpt-5.4`: adjusted `p = 0.00894`
- `gpt-5.1 > gpt-4.1`: adjusted `p = 0.02172`
- `gpt-5.1 vs gpt-5.2`: not significant after correction
- all other pairwise comparisons were not significant

Secondary descriptive support:
- `gpt-5.1` also had the highest mean final territory count at `19.38`
- the next best model, `gpt-5.2`, averaged `9.53`

That is enough to reject the global null on the benchmark that matters most here: actual game wins.

Under the strict all-pairs family, the conservative practical conclusion is:
- under this `90s planning + 90s execution + 15s placement` strategic condition, `gpt-5.1` is the strongest current full-stack OpenAI live-turn baseline
- but the win-only evidence does **not yet** cleanly separate `gpt-5.1` from `gpt-5.2` after multiple-comparison correction

Under the narrower confirmatory framing that matches why the second replicate was run, the result is stronger:
- `gpt-5.1` versus `gpt-5.2` is significant on wins after Holm correction within the `gpt-5.1`-vs-rest family
- that makes the combined `32`-game result a real confirmation of the earlier `16`-game signal, not just a descriptive impression

## Descriptive Outcomes

Batch-level summary:
- games completed: `32 / 32`
- mean rounds: `10.78`
- mean elapsed seconds: `2898.60`

The `mean_turn_time_seconds` metric below is accumulated LLM decision time per game, not literal wall-clock time per turn.

### Primary Win Table

| Player | Wins | Mean Final Territories | Mean Strategic Score | Mean Turn Time (s) | Mean Fallback Count | Mean Timed-Out Turns / Game |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 18 | 19.38 | 4.801 | 928.31 | 5.78 | 4.06 |
| `gpt-5.2` | 7 | 9.53 | 4.843 | 719.28 | 2.91 | 1.88 |
| `gpt-5.4` | 3 | 7.09 | 4.516 | 1101.25 | 13.81 | 7.50 |
| `gpt-4.1` | 4 | 6.00 | 4.611 | 149.51 | 0.00 | 0.00 |

Key read:
- `gpt-5.1` led the field decisively on raw wins
- `gpt-5.2` had the highest mean strategic score, not `gpt-5.1`
- `gpt-5.1` still converted that strategic quality into actual wins better than the rest
- `gpt-5.4` was the slowest and least operationally stable model in the batch

### Execution and Board-Conversion Metrics

| Player | Mean Successful Attacks / Game | Mean Successful Attacks / Turn | Mean Successful Attacks / Attacking Turn | Mean Failed Attacks / Game | Mean Failed Attacks / Turn | Mean Attack-Turn Rate | Mean Territory Delta / Turn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 42.56 | 4.198 | 4.198 | 8.38 | 0.789 | 1.000 | 4.198 |
| `gpt-5.2` | 34.75 | 3.627 | 3.650 | 7.84 | 0.814 | 0.993 | 3.627 |
| `gpt-5.4` | 25.97 | 2.724 | 2.763 | 3.00 | 0.330 | 0.986 | 2.724 |
| `gpt-4.1` | 29.53 | 3.315 | 3.377 | 18.59 | 2.086 | 0.978 | 3.315 |

Important nuance:
- `gpt-5.4`'s low failed-attack count is **not** evidence that it attacked better
- it attacked less successfully overall and also timed out far more often, so many turns ended before long attack chains could even happen

### Invalid Moves and Phase Errors

| Player | Mean Invalid Actions / Game | Mean Placement Errors / Game | Mean Attack Errors / Game | Mean Fortify Errors / Game | Mean Card-Trade Errors / Game |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 1.69 | 1.69 | 0.00 | 0.00 | 0.00 |
| `gpt-5.2` | 1.03 | 1.03 | 0.00 | 0.00 | 0.00 |
| `gpt-5.4` | 6.28 | 6.28 | 0.00 | 0.00 | 0.00 |
| `gpt-4.1` | 1.06 | 0.03 | 0.81 | 0.22 | 0.00 |

Interpretation:
- `gpt-5.4`'s main error mode was placement instability, not attack parsing
- `gpt-4.1` was the opposite: almost no placement trouble, but much noisier attack execution

### Mean LLM Call Times By Phase

| Player | Planning (s) | Placement (s) | Attack (s) | Fortify (s) |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 20.76 | 8.66 | 8.21 | 6.27 |
| `gpt-5.2` | 13.30 | 8.65 | 7.04 | 5.42 |
| `gpt-5.4` | 23.81 | 11.64 | 13.94 | 8.42 |
| `gpt-4.1` | 1.55 | 1.63 | 1.35 | 1.32 |

This is the clearest operational explanation for `gpt-5.4`:
- it was slowest in every important live phase
- it was especially slow in planning, placement, and attack
- the clock then punished it repeatedly

### Fallback and Timeout Concentration

Fallback counts by phase:

| Player | Planning | Placement | Attack | Fortify | Card Trade |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 1 | 54 | 117 | 13 | 0 |
| `gpt-5.2` | 0 | 33 | 43 | 17 | 0 |
| `gpt-5.4` | 0 | 201 | 234 | 6 | 1 |
| `gpt-4.1` | 0 | 0 | 0 | 0 | 0 |

Timeout counts by phase:

| Player | Planning | Placement | Attack | Fortify | Card Trade |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.1` | 1 | 54 | 117 | 13 | 0 |
| `gpt-5.2` | 0 | 33 | 43 | 15 | 0 |
| `gpt-5.4` | 0 | 201 | 231 | 6 | 1 |
| `gpt-4.1` | 0 | 0 | 0 | 0 | 0 |

This makes the `gpt-5.4` story concrete:
- the model was not just slightly slower
- it was catastrophically more timeout-prone in the repeated execution phases that matter most for Risk

## Statistical Results

### Primary Win-Based Omnibus Test

Winner-label permutation test:
- statistic: between-model separation in win counts across the `32` scheduled games
- Monte Carlo draws: `100,000`
- result: `p = 0.000485`

Decision:
- reject `H0`

### Post-Hoc Pairwise Win Tests

These tests condition on games won by either member of the pair and use an exact two-sided binomial test under the null that both models are equally likely to be the winner when one of them wins.

| Pair | Wins (A-B) | Raw p | Holm-Adjusted p |
| --- | ---: | ---: | ---: |
| `gpt-5.1 vs gpt-4.1` | 18-4 | 0.00434 | 0.02172 |
| `gpt-5.1 vs gpt-5.2` | 18-7 | 0.04329 | 0.17314 |
| `gpt-5.1 vs gpt-5.4` | 18-3 | 0.00149 | 0.00894 |
| `gpt-5.2 vs gpt-4.1` | 7-4 | 0.54883 | 1.00000 |
| `gpt-5.2 vs gpt-5.4` | 7-3 | 0.34375 | 1.00000 |
| `gpt-5.4 vs gpt-4.1` | 3-4 | 1.00000 | 1.00000 |

Interpretation:
- the evidence supports `gpt-5.1` beating `gpt-5.4` and `gpt-4.1` on the primary win benchmark
- the evidence does **not** yet separate `gpt-5.1` from `gpt-5.2` cleanly on wins after multiple-comparison correction
- the evidence also does not separate `gpt-5.2`, `gpt-5.4`, and `gpt-4.1` cleanly from one another on wins

Why this strict family can be too blunt here:
- this family answers the broad question "which of all `6` unordered pairs differ?"
- that was not the actual unresolved question after the first `16` games
- the actual unresolved question was whether the apparent `gpt-5.1 > gpt-5.2` edge would hold up in a follow-up replicate

### Focused Confirmatory `gpt-5.1`-Vs-Rest Family

If we restrict the post-hoc family to the comparisons that match the real follow-up question,
- `gpt-5.1 vs gpt-5.4`
- `gpt-5.1 vs gpt-4.1`
- `gpt-5.1 vs gpt-5.2`

then Holm-adjusted two-sided p-values are:

| Pair | Raw p | Holm-Adjusted p Within `gpt-5.1`-Vs-Rest Family |
| --- | ---: | ---: |
| `gpt-5.1 vs gpt-5.4` | 0.00149 | 0.00447 |
| `gpt-5.1 vs gpt-4.1` | 0.00434 | 0.00869 |
| `gpt-5.1 vs gpt-5.2` | 0.04329 | 0.04329 |

This is the framing that best matches the actual experimental sequence:
1. first `16` games produced a visible `gpt-5.1` lead
2. `gpt-5.1` versus `gpt-5.2` remained the main unresolved comparison
3. the second `16` games were run to resolve that exact issue
4. the combined `32`-game result still favors `gpt-5.1`, and under this focused family the `gpt-5.1 > gpt-5.2` win signal survives correction

Additional directional detail:
- conditioning only on wins by either `gpt-5.1` or `gpt-5.2`, the observed split is `18-7`
- raw one-sided binomial probability under equal strength: `p = 0.02164`
- raw two-sided binomial probability: `p = 0.04329`

This does **not** mean the broader all-pairs family was wrong.
It means the answer depends on which inferential family you think the experiment was actually designed to resolve.

### Secondary Territory-Based Strength Check

Blocked permutation on final territories remained strongly supportive:
- omnibus `p < 0.00001`
- Holm-corrected pairwise support:
  - `gpt-5.1 > gpt-5.4`
  - `gpt-5.1 > gpt-5.2`
  - `gpt-5.1 > gpt-4.1`

Interpretation:
- this secondary result supports the descriptive claim that `gpt-5.1` was also controlling more of the board when games ended
- but it is secondary because the models are instructed to win by reaching the `65%` control threshold, not to optimize average final territory as a surrogate objective

### Supporting Winner-Count Sanity Check

This is not the main multi-model inferential test, but it is directionally useful.

If each model had an equal `25%` chance to win each game, `gpt-5.1` getting `18` wins in `32` games would have a simple binomial upper-tail probability of approximately:
- `p = 0.00016`

That does not replace the omnibus winner-label permutation test, but it points the same way.

### Exploratory Execution Tests

Blocked permutation tests on mean successful attacks per turn:
- `gpt-5.1 > gpt-5.4`: `p < 0.00002`
- `gpt-5.1 > gpt-4.1`: `p = 0.00082`
- `gpt-5.1 > gpt-5.2`: `p = 0.00706`
- `gpt-5.2 > gpt-5.4`: `p = 0.00002`

These are exploratory rather than the formal primary endpoint, but they matter because they line up with the practical game story:
- `gpt-5.1` was better at converting turns into successful attack chains

## Seat Check

Seat rotation does not explain the result away.

`gpt-5.1` mean final territories by seat:
- seat 1: `16.88` with `3` wins
- seat 2: `16.50` with `3` wins
- seat 3: `25.25` with `7` wins
- seat 4: `18.88` with `5` wins

By contrast:
- `gpt-4.1` was heavily seat-sensitive and only won from seats `2` and `3`
- `gpt-5.4` never won from seats `2` or `3`

So this was not just a one-seat artifact.

## Average Successful Attacks By Round

These averages are pooled over both replicates. Late rounds are sparse because fewer games survive that long, so rounds `4` through `9` are the most interpretable midgame window.

| Round | `gpt-5.1` | `gpt-5.2` | `gpt-5.4` | `gpt-4.1` |
| --- | ---: | ---: | ---: | ---: |
| 1 | 4.781 | 5.875 | 3.719 | 5.625 |
| 2 | 4.156 | 3.031 | 3.500 | 2.875 |
| 3 | 3.031 | 1.969 | 2.438 | 2.062 |
| 4 | 3.625 | 3.161 | 2.594 | 2.290 |
| 5 | 3.871 | 2.700 | 2.484 | 2.857 |
| 6 | 4.267 | 3.111 | 2.444 | 3.545 |
| 7 | 5.115 | 2.957 | 2.304 | 3.684 |
| 8 | 4.348 | 3.882 | 2.429 | 3.875 |
| 9 | 4.100 | 4.118 | 2.529 | 3.375 |
| 10 | 3.500 | 3.600 | 2.533 | 4.231 |
| 11 | 3.562 | 5.214 | 2.692 | 2.889 |
| 12 | 4.357 | 4.833 | 2.583 | 5.000 |
| 13 | 4.077 | 5.727 | 3.000 | 3.375 |
| 14 | 5.333 | 4.700 | 1.625 | 6.833 |
| 15 | 1.000 | 1.000 | 1.000 | 1.000 |

Midgame read:
- `gpt-5.1` is strongest and most stable across the rounds where most games are still competitive
- `gpt-5.2` has some very strong late surviving rounds, but it does not match `gpt-5.1`'s overall conversion consistency
- `gpt-5.4` lags badly almost everywhere outside the opener

## Why `gpt-5.1` Won

The easiest wrong explanation would be:
- "`gpt-5.1` must just be the smartest planner"

The data do **not** support that as the full story.

What the data actually say:

1. `gpt-5.2` had the highest mean strategic score.
   - `gpt-5.2`: `4.843`
   - `gpt-5.1`: `4.801`

2. `gpt-5.1` was the best executor by a meaningful margin.
   - highest successful attacks per game: `42.56`
   - highest successful attacks per turn: `4.198`
   - highest territory delta per turn: `4.198`
   - full attack-turn rate: `1.000`

3. `gpt-5.4` was too slow for the environment.
   - slowest planning, placement, and attack call times
   - far too many placement and attack timeouts
   - far too many fallback responses

4. `gpt-4.1` was fast and clean, but too tactically lossy.
   - zero fallbacks and zero timeouts
   - but `18.59` failed attacks per game
   - and much lower final territory totals than `gpt-5.1`

The most defensible combined explanation is:
- `gpt-5.1` sits at the best strength/latency tradeoff for this exact game loop
- it plans well enough
- it executes attack chains better than the others
- and unlike `gpt-5.4`, it does not burn so much clock that the engine regularly destroys its own turn with forced fallbacks

## Why `gpt-5.4` Lost

This result should **not** be summarized as:
- "`gpt-5.4` is less capable than `gpt-5.1` in general"

What this experiment actually supports is narrower:
- `gpt-5.4` is a poor fit for this synchronous multi-call Risk loop under these timers

The evidence chain is direct:
- it had the slowest mean planning calls: `23.81s`
- it had the slowest mean placement calls: `11.64s`
- it had the slowest mean attack calls: `13.94s`
- it timed out `7.5` turns per game on average
- most of those failures concentrated in `troop_placement` and `attack`

That means `gpt-5.4` is often still spending clock on placement and early attack decisions while the better live players are already converting the board.

Its low failed-attack count is therefore misleading:
- it is not failing less because it attacks better
- it is often doing less because the turn collapses earlier

## Practical Decision

For the strategic live-turn condition used here:
- promote `gpt-5.1` to the current working full-stack OpenAI baseline
- treat `gpt-5.2` as the best current planning-only hybrid candidate
- do not use `gpt-5.4` as the default full-stack OpenAI tournament representative under this policy

Important nuance:
- if you insist on the broadest possible all-pairs correction family, `gpt-5.1` versus `gpt-5.2` remains short of that bar
- if you use the narrower family that matches the actual follow-up question, the combined `32` games do support `gpt-5.1 > gpt-5.2` on wins

## Follow-On Recommendation

The next correct experiment is the planning-only hybrid showdown:
- `gpt-5.1` full stack
- `gpt-5.5` planning + `gpt-5.1` execution
- `gpt-5.4` planning + `gpt-5.1` execution
- `gpt-5.2` planning + `gpt-5.1` execution

Reason:
- this `32`-game result makes `gpt-5.1` the right execution baseline
- it does **not** prove that `gpt-5.1` is also the best planner
- `gpt-5.2` remains the strongest current planning candidate by the rubric score
