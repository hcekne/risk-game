# OpenAI 5.1 Execution Hybrid Planning Showdown

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `openai_51_execution_hybrid_planning_showdown_16`
- Raw local artifacts:
  - `/shared-game-results/experiments/experiment__2026-05-03_20-35-06__openai_51_execution_hybrid_planning_showdown_16`
- Core files:
  - `experiment_results.json`
  - `experiment_summary.json`
  - `experiment_summary.md`
  - per-game `turn_summary_turn_*.json`

## Research Question

If `gpt-5.1` is already the strongest full-stack OpenAI live-turn player, can a stronger planning model improve it further when only the pre-turn planning call is swapped out?

More concretely:
- does `gpt-5.2`, `gpt-5.4`, or `gpt-5.5` produce a better planning signal than `gpt-5.1` itself?
- does any planning-only hybrid beat the `gpt-5.1-full` baseline on the metric that matters here: actual game wins?
- are any apparent differences large enough to survive skeptical scrutiny, or are they easily explained by chance?

## Design

- Conditions:
  - `gpt-5.1-full`
  - `gpt-5.5-plan / gpt-5.1-exec`
  - `gpt-5.4-plan / gpt-5.1-exec`
  - `gpt-5.2-plan / gpt-5.1-exec`
- Games: `16`
- Seats: `4-player`, seat-rotated
- Rules:
  - progressive cards enabled
  - territory control win threshold `65%`
  - max rounds `15`
  - isolated planning timer `90s`
  - shared execution turn timer `90s`
  - placement timer `15s`
  - execution model in all hybrid variants: `gpt-5.1`
  - execution phase profile:
    - placement `medium`
    - attack `medium`
    - fortify `medium`
    - card trade `low`
  - planning phase profile:
    - planning `high`

Important methodological note:
- this is a **planner-only ablation**
- the execution engine is held constant at `gpt-5.1` for the three hybrid variants
- that sharply reduces variance from execution quality, but it also compresses the total effect size any planner swap can realistically produce

## Analysis Method

Primary endpoint:
- wins under the configured `65%` territory-control rule

Secondary diagnostics:
- final territory totals
- successful attacks per game and per turn
- failed attacks per game and per turn
- fallback counts and timeouts by phase
- planning latency and planning-text style

How the metrics were computed:
- win counts, seat order, final territories, turn times, and per-game summaries were read from `experiment_results.json`
- per-turn attack, timeout, fallback, and planning details were recomputed from the saved `turn_summary_turn_*.json` files
- pairwise win tests use exact two-sided binomial tests conditioned on games won by either member of the pair
- the omnibus win test uses a Monte Carlo winner-label permutation under the equal-strength null
- planning-phase qualitative summaries are based on the saved `pre_turn_planning` raw responses, not on reconstructed prompts

## Hypotheses

Primary omnibus question:
- `H0`: all four variants are equally likely to win
- `H1`: at least one variant differs

Main practical follow-up:
- does any planning-only hybrid beat `gpt-5.1-full` clearly enough to justify replacing the simpler baseline?

Prior-sensitive follow-up:
- if a skeptic enters with a prior like `gpt-5.5 > gpt-5.4 > gpt-5.2 > gpt-5.1`, does this experiment provide enough evidence to support that order?

## Core Result

It does not.

Win counts:
- `gpt-5.2-plan / gpt-5.1-exec`: `5 / 16`
- `gpt-5.1-full`: `4 / 16`
- `gpt-5.5-plan / gpt-5.1-exec`: `4 / 16`
- `gpt-5.4-plan / gpt-5.1-exec`: `3 / 16`

Primary omnibus win test:
- winner-label permutation test: `p = 0.985`

Interpretation:
- this batch is almost maximally compatible with equal win probabilities
- the observed `5 / 4 / 4 / 3` split is so balanced that it is not evidence of meaningful separation

Secondary territory test:
- blocked permutation omnibus on final territories: `p = 0.653`

That means both the primary benchmark and the main descriptive backup metric point the same way:
- **no planning winner is established**

## Why The Win Differences Are Easily Explained By Chance

This is the most important section of the note.

### Under a simple equal-strength null

If all four variants are equally likely to win each of the `16` games:

- the expected win vector is `4 / 4 / 4 / 4`
- the observed vector is `5 / 4 / 4 / 3`

That is extremely ordinary.

Useful null probabilities:
- probability that the top variant gets at least `5` wins: `0.985`
- probability of seeing the sorted pattern `5 / 4 / 4 / 3` exactly: `0.140`
- probability that the range between top and bottom is at most `2` wins: `0.210`

So:
- seeing one planner end on `5` wins is not surprising
- seeing another end on `3` wins is not surprising
- the whole batch looks like normal finite-sample noise under equality

### Pairwise win tests

| Pair | Wins (A-B) | Raw Two-Sided p |
| --- | ---: | ---: |
| `gpt-5.2-plan` vs `gpt-5.5-plan` | `5-4` | `1.00000` |
| `gpt-5.2-plan` vs `gpt-5.1-full` | `5-4` | `1.00000` |
| `gpt-5.2-plan` vs `gpt-5.4-plan` | `5-3` | `0.72656` |
| `gpt-5.5-plan` vs `gpt-5.1-full` | `4-4` | `1.00000` |
| `gpt-5.5-plan` vs `gpt-5.4-plan` | `4-3` | `1.00000` |
| `gpt-5.1-full` vs `gpt-5.4-plan` | `4-3` | `1.00000` |

None of these are even close to a meaningful win-based separation.

## Descriptive Outcomes

Batch summary:
- games completed: `16 / 16`
- mean rounds: `9.38`
- mean elapsed seconds: `2746.42`

### Main Performance Table

| Player | Wins | Mean Final Territories | Mean Strategic Score | Mean Turn Time (s) | Mean Fallback Count | Mean Timed-Out Turns / Game |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.2-plan / 5.1-exec` | 5 | 13.44 | 4.801 | 753.49 | 5.75 | 4.25 |
| `gpt-5.5-plan / 5.1-exec` | 4 | 10.69 | 4.779 | 618.89 | 3.69 | 2.75 |
| `gpt-5.4-plan / 5.1-exec` | 3 | 9.56 | 4.645 | 760.49 | 4.12 | 3.12 |
| `gpt-5.1-full` | 4 | 8.31 | 4.766 | 613.32 | 2.69 | 2.00 |

Descriptive read:
- `gpt-5.2` planning looks best by raw wins and territories
- `gpt-5.5` planning is close behind and cleaner operationally
- `gpt-5.4` planning is the weakest descriptively
- but none of those gaps are large enough to support a strong claim

### Attack and Board-Conversion Metrics

| Player | Mean Successful Attacks / Game | Mean Successful Attacks / Turn | Mean Successful Attacks / Attacking Turn | Mean Failed Attacks / Game | Mean Failed Attacks / Turn | Mean Attack-Turn Rate | Mean Territory Delta / Turn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.2-plan / 5.1-exec` | 33.56 | 3.784 | 3.784 | 5.69 | 0.691 | 1.000 | 3.784 |
| `gpt-5.5-plan / 5.1-exec` | 29.94 | 3.769 | 3.769 | 5.81 | 0.744 | 1.000 | 3.769 |
| `gpt-5.4-plan / 5.1-exec` | 29.31 | 3.174 | 3.251 | 6.44 | 0.773 | 0.975 | 3.174 |
| `gpt-5.1-full` | 28.25 | 3.474 | 3.474 | 5.38 | 0.671 | 1.000 | 3.474 |

Interpretation:
- `gpt-5.2` planning produced the best descriptive attack conversion
- `gpt-5.5` planning was almost identical on attacks per turn
- `gpt-5.4` planning trailed the others
- because all hybrid variants use the same `gpt-5.1` executor, these differences are necessarily modest

### Invalid Moves and Phase Errors

| Player | Mean Invalid Actions / Game | Mean Placement Errors / Game | Mean Attack Errors / Game | Mean Fortify Errors / Game | Mean Card-Trade Errors / Game |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.2-plan / 5.1-exec` | 1.50 | 1.50 | 0.00 | 0.00 | 0.00 |
| `gpt-5.5-plan / 5.1-exec` | 0.81 | 0.81 | 0.00 | 0.00 | 0.00 |
| `gpt-5.4-plan / 5.1-exec` | 1.06 | 1.00 | 0.00 | 0.00 | 0.00 |
| `gpt-5.1-full` | 0.69 | 0.69 | 0.00 | 0.00 | 0.00 |

Again, no clear planner separation:
- `gpt-5.2` planning was strongest descriptively on results, but it also induced the most invalid/placement trouble downstream

### Fallback and Timeout Concentration

Fallbacks by phase:

| Player | Planning | Placement | Attack | Fortify | Card Trade |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.2-plan / 5.1-exec` | 0 | 24 | 60 | 8 | 0 |
| `gpt-5.5-plan / 5.1-exec` | 1 | 13 | 42 | 2 | 1 |
| `gpt-5.4-plan / 5.1-exec` | 0 | 16 | 44 | 6 | 0 |
| `gpt-5.1-full` | 0 | 11 | 32 | 0 | 0 |

Timeouts by phase are almost identical to the fallback counts because the fallbacks are mainly timeout-driven in this batch.

Operational read:
- `gpt-5.2` planning produced the heaviest downstream execution burden
- `gpt-5.5` planning was more operationally efficient
- `gpt-5.4` planning did not earn its extra planning cost

## Planning-Phase Behavior

### Planning latency and response size

| Player | Mean Planning Time (s) | Mean Planning Response Length |
| --- | ---: | ---: |
| `gpt-5.2-plan / 5.1-exec` | 14.47 | 300.41 |
| `gpt-5.5-plan / 5.1-exec` | 16.07 | 177.35 |
| `gpt-5.4-plan / 5.1-exec` | 24.76 | 253.87 |
| `gpt-5.1-full` | 17.95 | 339.88 |

Immediate read:
- `gpt-5.4` was the slowest planner by a wide margin
- `gpt-5.5` was the most concise planner
- `gpt-5.2` was the fastest of the hybrid planners

### Qualitative planning profiles

#### `gpt-5.2` planner

This planner most often produced:
- a main hammer plus a backup line
- explicit hold/choke instructions
- continent-aware consolidation plans
- multi-step sequences that looked like “take territory, then fortify back to the choke”

Representative traits from the saved plans:
- “main hammer”
- “backup”
- “hold the choke”
- sweep one line, then centralize survivors

This was the most position-building planner in the batch.

#### `gpt-5.5` planner

This planner most often produced:
- short local-best-line plans
- one clear attack chain
- one clear “avoid bad front” instruction
- simple border-hold fortify advice

Representative traits:
- concise
- local
- executor-friendly
- less branching than `gpt-5.2`

This looked like the cleanest low-complexity planner.

#### `gpt-5.4` planner

This planner most often produced:
- region-completion plans
- straightforward linear chains
- slower planning without obvious extra payoff
- less adaptive-looking backup structure than `gpt-5.2`

Representative traits:
- “finish Europe”
- “finish Australia”
- linear follow-through
- relatively expensive planning time

This was the least compelling planner in the batch.

#### `gpt-5.1-full`

This planner most often produced:
- opportunistic expansion
- bonus-breaking if convenient
- cheap border picks
- centralization and consolidation rather than elaborate positional scaffolding

Representative traits:
- break weak bonuses
- take cheap adjacent territory
- centralize surviving stack
- avoid large enemy fronts

It looked pragmatic and flexible, but less architected than `gpt-5.2`.

## Prior-Sensitive Interpretation

This experiment is weak enough that the answer depends heavily on what prior you bring into it.

### Prior 1: all variants equal

The data are very comfortable under this prior.

Evidence:
- omnibus win p-value `0.985`
- exact sorted win pattern `5 / 4 / 4 / 3` occurs with probability about `0.140` under equal strength
- the top variant getting at least `5` wins happens with probability about `0.985`

So if your prior was “all four variants are equal,” this batch gives you no reason to move far away from that position.

### Prior 2: `gpt-5.5 > gpt-5.4 > gpt-5.2 > gpt-5.1`

As stated, that is not a full probabilistic model. It is only a rank ordering. To do formal Bayesian model comparison, you would need effect-size assumptions too.

Still, the batch does **not** support that order.

Observed win order:
- `gpt-5.2`: `5`
- `gpt-5.5`: `4`
- `gpt-5.1`: `4`
- `gpt-5.4`: `3`

So the observed data do not even line up directionally with the proposed prior ordering.

Using a neutral Dirichlet posterior over win probabilities, the posterior probability of the exact order
- `gpt-5.5 > gpt-5.4 > gpt-5.2 > gpt-5.1`

is only about:
- `0.0256`

Posterior probability each variant is actually the best:
- `gpt-5.2-plan / 5.1-exec`: `0.412`
- `gpt-5.5-plan / 5.1-exec`: `0.235`
- `gpt-5.1-full`: `0.235`
- `gpt-5.4-plan / 5.1-exec`: `0.118`

That does **not** mean `gpt-5.2` is proven best. It means the posterior mass is still diffuse, with `gpt-5.2` only modestly ahead.

### Illustrative likelihood comparison

Because the ordered prior needs effect sizes, here are two illustrative ordered win-probability models for the order `5.5 > 5.4 > 5.2 > 5.1`:

- mild ordered prior: `(0.31, 0.27, 0.23, 0.19)`
- strong ordered prior: `(0.40, 0.30, 0.20, 0.10)`

Relative likelihood of the observed wins `[4, 3, 5, 4]` compared with the equal-strength model `(0.25, 0.25, 0.25, 0.25)`:

- mild ordered prior: likelihood ratio `0.655`
- strong ordered prior: likelihood ratio `0.095`

Interpretation:
- the observed data are better explained by equality than by those illustrative ordered priors
- the stronger the ordered prior, the worse it fits the data

## Decision

This experiment does **not** establish that:
- `gpt-5.2` is a better planner than `gpt-5.5`
- any hybrid is better than `gpt-5.1-full`
- `gpt-5.5` planning is worse than `gpt-5.2` planning

What it does support:
- `gpt-5.4` planning remains the least attractive of the three planner swaps
- `gpt-5.2` and `gpt-5.5` are both plausible planning candidates
- the evidence is too weak to separate them confidently
- a skeptic can reasonably explain the current win differences as chance

## Practical Conclusion

If forced to choose today:
- `gpt-5.5` remains fully defensible as a planner on prior grounds
- `gpt-5.2` has a slight descriptive edge in this one batch
- but the batch is not strong enough to claim `gpt-5.2 > gpt-5.5`

So the current honest position is:
- `gpt-5.2-plan / gpt-5.1-exec`
- `gpt-5.5-plan / gpt-5.1-exec`
- `gpt-5.1-full`

are all still effectively unresolved at this sample size.

## Follow-On Recommendation

Do not widen the planner field again.

If the goal is to decide whether `gpt-5.2` or `gpt-5.5` is the better planning model over `gpt-5.1` execution, run a direct playoff:

- `gpt-5.2-plan / gpt-5.1-exec`
- `gpt-5.5-plan / gpt-5.1-exec`
- optionally `gpt-5.1-full` as a baseline anchor

Recommended size:
- `32` more games minimum
- `48-64` if the goal is a skeptic-resistant win-based claim
