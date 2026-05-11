# Experiment Program

This document defines the first serious experiment program for the Risk project.

It is designed to answer a small number of high-value questions under realistic budget and time constraints, while still producing results that are defensible enough to use in a follow-up article.

For completed tracked write-ups from this program, use the suite archive under [docs/experiment-suites/README.md](experiment-suites/README.md).

## Program Update: 2026-05-07

The first round of scored experiments has changed the priorities of this program.

Current working conclusions:
- the OpenAI generation question is resolved enough for now: `gpt-5.1` is the current OpenAI live-turn baseline, and the cross-provider preset currently uses `gpt-5.1` execution plus `gpt-5.5` planning
- the balanced salvaged provider `16` and the clean direct provider `16` now agree on the headline result: Gemini won `10 / 16` in both
- the pooled `32`-game provider estimate currently favors `gemini-3.1-pro-preview` clearly over GPT-5.1, Claude, and Kimi
- `claude-opus-4-7` is currently the cleanest runtime baseline
- `kimi-k2.6` remains viable but trails the stronger closed-model representatives in this setting
- the first Kimi anchor batches now place Kimi roughly near the `gpt-4.1` tier and somewhat below `gemini-2.5-pro`

What this means for the next phase:
1. run Kimi capability-anchoring experiments against historical OpenAI, Gemini, and Anthropic anchors
2. only then spend more budget on representation ablations or learning experiments
3. keep future provider-wide reruns for cost-instrumented replication or roster changes, not to re-answer the basic winner question again

This also means the old short OpenAI-only baseline plan is no longer a top priority unless a new OpenAI release appears or a specific provider-side question reopens.

## Research Goal

Measure whether different frontier models show meaningful differences in observable strategic performance in Risk under a fixed ruleset, fixed prompt setup, and fixed runtime constraints.

The key idea is to compare models as **usable synchronous game agents**, not just as abstract language models.

That means:
- latency matters
- output reliability matters
- legality and format compliance matter
- a model that cannot reliably act within the turn loop is not a valid live-game competitor

## Why Open-vs-Closed Matters

This program is not only about ranking proprietary frontier models against each other.

It also needs to answer a broader strategic question:
- how far behind, at parity with, or occasionally ahead are strong open-weight or more openly deployable models compared with the best closed systems?

That matters for at least three reasons:
- sovereign-AI debates increasingly depend on whether states, labs, or institutions can achieve strategically useful capability without depending entirely on closed foreign APIs
- open-vs-closed gaps are often discussed in vague benchmark terms, but a multi-turn strategy game gives a more concrete operational test of planning, adaptation, and execution
- if `kimi-k2.6` performs competitively, that is a materially different story from “open models are still far behind”; if it lags, we want a clean estimate of how far back in model-generation terms it appears to be

For this reason, the Kimi track should not stop at “does it beat today’s closed leaders?” If needed, it should also try to locate Kimi relative to earlier closed-model anchor tiers across OpenAI, Google, and Anthropic.

## Shared Protocol

All main experiments should hold the following constant unless the experiment explicitly varies one of them.

### Rules and runtime

- Progressive cards: `on`
- Capitals mode: `off`
- Territory-control win threshold: `65%`
- Max rounds: `15`
- Full turn budget: `90s`
- Placement prompt budget: `15s`
- Default placement reasoning: `low`
- Default planning/attack/fortify reasoning: capped at `medium`
- Default card-trade reasoning: capped at `low`
- Opening setup remains alternating one troop at a time

### Agent policy controls

- Use the same baseline prompt pack for all compared agents.
- Use the same compact state representation for all compared agents.
- No between-game learning in the first program.
- No provider-specific tool advantage in the headline experiments unless every provider has an equivalent enabled.

### Primary and secondary outcomes

Primary endpoint:
- win count / win rate under the configured territory-control victory rule

Secondary endpoints:
- final territory share
- finish rank
- survival length
- invalid move rate
- fallback rate
- mean turn time
- strategic rubric score
- tracked input tokens
- tracked output tokens
- estimated API cost
- cost per win / win rate per dollar

### Cost estimation conventions

For cost-aware experiments, the repo estimates API spend from saved usage metadata plus the local pricing snapshot in [risk_game/utils/model_pricing.py](../risk_game/utils/model_pricing.py).

Current convention:
- uncached input tokens are priced at the model's input-token rate
- cached input tokens are priced at the model's cached-input rate where available
- output tokens are priced at the model's output-token rate
- these components are summed across all calls for each player

Important reporting rule:
- treat these as estimated costs, not ground-truth billing exports
- always report the pricing snapshot ID alongside any cost-per-win or strategy-per-dollar claim
- do not compare cost across old pre-instrumentation runs that have null usage fields

### Statistical approach

For each experiment:
- Pre-register one primary outcome: wins under the configured victory rule.
- Use one omnibus null hypothesis first.
- Then use planned pairwise winner comparisons.
- Treat final territory share and rubric as supporting evidence, not the sole headline metric.
- Report effect sizes and confidence intervals, not only p-values.

Recommended analysis methods:
- winner-label permutation test for the omnibus comparison
- exact binomial or sign-style tests for pairwise winner comparisons
- blocked permutation on final territory share as a secondary descriptive check
- bootstrap confidence intervals where useful

## Seat-Rotation Policy

Seat order matters, so every experiment must rotate seats.

### Three-player experiments

Budget target:
- `15` games total

Rotation scheme:
- repeat a 3-game cyclic seat rotation 5 times
- Example block:
  - Game 1: A / B / C
  - Game 2: B / C / A
  - Game 3: C / A / B

What this guarantees:
- each model starts first `5` times
- each model starts second `5` times
- each model starts third `5` times

Important note:
- `15` is a good budget target, but it does **not** perfectly balance all `6` possible full seat-order permutations.
- If perfect permutation balance becomes important later, use `18` games instead.
- For the first program, balancing starting seat exactly is the more important requirement.

### Four-player experiments

Budget target:
- `16` games total

Rotation scheme:
- repeat a 4-game cyclic seat rotation 4 times
- Example block:
  - Game 1: A / B / C / D
  - Game 2: B / C / D / A
  - Game 3: C / D / A / B
  - Game 4: D / A / B / C

What this guarantees:
- each model occupies each seat exactly `4` times

## Experiment 1: Generation Ladder

Question:
- Do newer OpenAI model generations play Risk better than older ones under the same live-turn constraints?

Lineup:
- `gpt-5.5`
- `gpt-5.4`
- `gpt-4.1`

Design:
- `3` players
- `15` games
- no learning between games

Primary null hypothesis:
- H0: win probability is equal across `gpt-5.5`, `gpt-5.4`, and `gpt-4.1`

Primary alternative hypothesis:
- H1: at least one model has a different win probability

Planned directional expectation:
- `gpt-5.5 > gpt-5.4 > gpt-4.1`

Why this experiment matters:
- It answers the cleanest public question: does a newer model generation actually produce stronger strategic play?

Status update on `2026-05-06`:
- the tracked strategic generation-ladder result is already sufficient to use `gpt-5.1` as the current OpenAI baseline for the rest of the program
- further OpenAI-only ladder work is now lower priority than confirmatory provider replication

## Experiment 2: Size Ladder

Question:
- Within one model family, how much does model size matter for strategic play?

Lineup:
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`

Design:
- `3` players
- `15` games
- no learning between games

Primary null hypothesis:
- H0: win probability is equal across the GPT-5.4 size variants

Primary alternative hypothesis:
- H1: at least one size variant has a different win probability

Planned directional expectation:
- `gpt-5.4 > gpt-5.4-mini > gpt-5.4-nano`

Why this experiment matters:
- It measures how much strategic capability scales with model size under the same prompt and rule environment.
- It is also one of the best cost-to-insight experiments in the whole program.

## Experiment 3: Reasoning-Budget Ladder

Question:
- Does extra thinking effort improve strategic performance for a usable lower-cost model?

Core lineup:
- `gpt-5.4-mini-none`
- `gpt-5.4-mini-low`
- `gpt-5.4-mini-medium`

Design:
- `3` players
- `15` games
- no learning between games

Primary null hypothesis:
- H0: win probability is equal across the three reasoning settings

Primary alternative hypothesis:
- H1: at least one reasoning setting has a different win probability

Planned directional expectation:
- `medium > low >= none`

Why this experiment matters:
- It isolates whether “thinking more” helps in a strategy game, or whether it mainly adds cost and latency.

Important note:
- `high` is intentionally excluded from the first pass so this stays a clean 3-player, 15-game experiment.
- If the first pass shows a clear benefit from more reasoning, `high` can be added later as a follow-up extension.

## Experiment 4: Cross-Provider Live-Turn Championship

Question:
- Which top usable model performs best in a live synchronous Risk setting across providers?

Provisional lineup:
- OpenAI: `gpt-5.1` execution plus `gpt-5.5` planning
- Anthropic: `claude-opus-4-7`
- Google: `gemini-3.1-pro-preview` as the chosen Google representative
- Moonshot: `kimi-k2.6` with thinking disabled for execution and planning-only thinking enabled where explicitly configured

Design:
- `4` players
- `16` games
- no learning between games
- every candidate must pass a smoke test before entering the full championship

Primary null hypothesis:
- H0: win probability is equal across the provider representatives

Primary alternative hypothesis:
- H1: at least one provider representative has a different win probability

Directional expectation:
- no directional ordering should be pre-registered here

Why this experiment matters:
- This is the main “who is strongest right now in usable live play?” experiment.

Important constraint:
- This is a **usable live-turn** championship, not a “best model in the abstract” championship.
- A model that is too slow, too unstable, or too format-fragile to function as a synchronous player should be excluded on methodological grounds.
- For this reason, `kimi-k2.6` should only enter with thinking disabled, and `gpt-5.5-pro` remains excluded from synchronous live-turn play.

Status update on `2026-05-07`:
- the balanced salvaged `16`-game strategic provider result has now been followed by a clean direct `16`-game replicate
- Gemini won `10 / 16` in both blocks
- the pooled `32`-game result is now strong enough to treat Gemini as the current best provider representative under this frozen condition
- future provider work should now shift from “who wins this roster?” to “why does Gemini win?” and “where exactly does Kimi sit relative to older closed-model anchor tiers?”

## Experiment 5: Kimi Capability Anchoring

Question:
- If `kimi-k2.6` is not clearly the strongest in the cross-provider field, where does it sit relative to earlier closed-model anchor tiers?

Core idea:
- The cross-provider championship tells us whether Kimi is competitive with the current closed frontier.
- This fifth experiment tells us how to interpret the result if it is not.
- It is an anchoring experiment: it tries to locate Kimi on a rough strategic-capability timeline.
- The defensible claim here is about **capability tier**, not literal calendar months. Different providers expose different archived models on different schedules, so "three months behind" should be treated as a public shorthand rather than the primary statistical claim.

When to run it:
- run this after a clean confirmatory replicate of Experiment 4
- prioritize it if `kimi-k2.6` is clearly weaker than the best closed models but still appears competent and live-turn viable
- if `kimi-k2.6` wins or ties for the top in Experiment 4, this experiment becomes optional rather than mandatory

Anchor families:

### First-pass design choice

The first pass should use duplicate-team `2x2` arenas, not mixed provider ladders.

Why:
- it isolates one anchor family at a time
- it reduces idiosyncratic single-player variance by measuring family-vs-family strength
- it makes the public claim cleaner: “two Kimi agents versus two copies of a single historical anchor”
- it lets the OpenAI, Gemini, and Anthropic anchor batches run in parallel without changing the interpretation of any one result

Shared design:
- `4` players
- `16` games
- `2` copies of `kimi-k2.6`
- `2` copies of one anchor model family
- same strategic `90 / 90 / 15` condition used in the provider championship

### 5A. OpenAI anchor team arena

Question:
- Is `kimi-k2.6` closer to the current OpenAI live-turn baseline or to an earlier GPT tier?

First-pass lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `gpt-4.1-a`
- `gpt-4.1-b`

Why this anchor:
- `gpt-4.1` is a clean older OpenAI tier that remains accessible and strategically meaningful in this repo
- if Kimi cannot match a duplicated `gpt-4.1` team under the same live condition, then “only a few months behind frontier” becomes much less credible in this environment

Optional extension:
- if the first pass suggests Kimi sits clearly above or clearly below `gpt-4.1`, add a second OpenAI team arena against `gpt-5.2` or another still-live intermediate anchor

### 5B. Gemini anchor team arena

Question:
- Is `kimi-k2.6` closer to the current Gemini live-turn baseline or to an earlier stable Gemini tier?

First-pass lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `gemini-2.5-pro-a`
- `gemini-2.5-pro-b`

Why this anchor:
- `gemini-2.5-pro` is the strongest still-accessible older Gemini anchor already supported in the repo
- this is the cleanest way to ask whether Kimi is actually near Google’s current live frontier or still notably below it

Status update on `2026-05-08`:
- the first duplicated-team `2x2` Gemini anchor run is complete
- `gemini-2.5-pro` beat `kimi-k2.6` `9-7`
- that is a real directional edge, but not yet a large or decisive gap on wins alone
- taken together with the GPT-4.1 anchor result, the current reading is that Kimi sits above-or-around the GPT-4.1 band but below Gemini 2.5 Pro in this environment
- this makes the public-facing “Kimi is only a few months behind current frontier models” story look too optimistic for live strategic play

### 5C. Anthropic anchor team arena

Question:
- Is `kimi-k2.6` closer to the current Claude frontier representative or to an older Anthropic tier?

First-pass lineup:
- `kimi-k2.6-a`
- `kimi-k2.6-b`
- `claude-sonnet-4-20250514-a`
- `claude-sonnet-4-20250514-b`

Why this anchor:
- `claude-sonnet-4-20250514` is a still-accessible older Anthropic anchor that is cheaper and easier to deploy than the older Opus snapshots
- it gives a cleaner family-level anchor than mixing current and historical Claude variants in one batch

Status update on `2026-05-08`:
- the first duplicated-team `2x2` Anthropic anchor run is complete
- `kimi-k2.6` beat `claude-sonnet-4-20250514` `9-7`
- that is not a decisive win-based separation, but it does show Kimi is fully competitive with this older Sonnet tier
- more importantly, Kimi is far cheaper and much less timeout-prone under the shared live harness
- a newer Sonnet 4.5 follow-up was also tried, but it should be treated as archived rather than as main evidence because the runtime mismatch is too severe and the pricing table is incomplete for that model

Primary null hypothesis:
- H0: family-level win probability is equal across the two Kimi copies and the two anchor copies in the chosen team arena

Primary alternative hypothesis:
- H1: the Kimi team and the anchor team do not have equal win probability under the same frozen live strategic condition

Interpretive goal:
- not just “did Kimi win?”
- instead: does Kimi look closer to the current closed frontier, an earlier provider tier, or clearly below that when the comparison is made against a duplicated anchor family under the same ecology?

Why this experiment matters:
- It is the clearest way to translate a cross-provider result into a statement people will actually care about.
- It supports the sovereign-AI question directly by estimating how much strategic capability can currently be accessed outside the most closed frontier systems.
- It produces a more nuanced conclusion than a simple provider leaderboard.

Important note:
- This experiment is especially valuable for article-writing because it lets us say things like:
- `kimi-k2.6` looked competitive with `gpt-4.1` but not with `gpt-5.1`
- `kimi-k2.6` looked closer to an earlier Gemini tier than to `gemini-3.1-pro-preview`
- `kimi-k2.6` looked competitive with an older Anthropic Sonnet tier, even if the win gap was not decisive
- Those are much more interpretable public claims than “Kimi finished second in one tournament.”
- Do not turn these into literal "months behind" claims unless the anchor grid and provider release timeline actually justify that translation.

## Model Viability Rules

Before any model enters a headline experiment, it must pass all of the following:

- paid completion canary works
- model can produce legal placement outputs
- model can complete live turns inside the configured timing policy
- model does not rely on persistent fallback behavior
- model does not require a provider-specific advantage unavailable to the comparison set

### Current important exclusion

`gpt-5.5-pro` should not be included in live synchronous experiments.

Reason:
- it is too slow or too reasoning-heavy for live-turn Risk play
- on actual saved Risk prompts, it consumed large output budgets entirely as reasoning tokens without emitting a move

That exclusion is a methodological decision, not a general statement that the model is weak.

See also:
- [development-log.md](development-log.md)

## Seed Policy

- Use a fixed seed bank per experiment and save it with the experiment metadata.
- Reuse the same seed bank for reruns of the same experiment design.
- Do not mix ad hoc seeds into a scored experiment batch once it has started.

## Reporting Template

Each experiment should report:
- lineup
- exact runtime settings
- seat-rotation schedule
- seed bank
- win rate by model
- win outcome by game
- final territory share by game
- mean and median finish rank
- invalid move rate
- fallback rate
- mean turn time
- strategic rubric average
- pairwise winner comparisons
- pairwise effect sizes on final territory share as a secondary diagnostic

## Kimi K2.6 Inference Recommendation

### Best path for benchmark purity

Use the official Moonshot API first.

Why:
- Moonshot presents K2.6 as its latest model on the official platform
- the API is OpenAI-compatible
- it uses the native vendor path rather than a routed hosting layer

Official references:
- Moonshot platform homepage: K2.6 is listed as the latest model with pricing and context notes
- Kimi quickstart docs: the API is OpenAI-compatible and uses `base_url="https://api.moonshot.ai/v1"`

Sources:
- [Moonshot Kimi platform](https://platform.moonshot.ai/)
- [Kimi API quickstart](https://platform.kimi.ai/docs/guide/kimi-k2-5-quickstart)

Practical implication:
- if Kimi enters the cross-provider championship, the first fair version should use the native Moonshot API, not a third-party router

### Best path for latency-focused engineering tests

Fireworks is the most interesting alternative host to test if native Kimi proves too slow for live play.

Why:
- Fireworks explicitly documents a `Kimi K2.6 Turbo` route for faster interactive use
- this is useful if the question becomes “what is the fastest usable deployment path for Kimi?” rather than “how does Moonshot-native Kimi compare to other providers?”

Important warning:
- Fireworks-hosted Kimi should be treated as a different deployment condition
- it should not silently replace Moonshot-native Kimi inside the main provider championship

Source:
- [Fireworks serverless priority and turbo docs](https://docs.fireworks.ai/guides/serverless-products)

### Recommended policy for this project

- For the cross-provider championship: use Moonshot-native `kimi-k2.6` if it passes smoke tests
- If native Moonshot Kimi fails the live-turn viability check, document that failure clearly
- If we still want to explore Kimi further, run a separate engineering experiment using Fireworks `Kimi K2.6 Turbo`

## Immediate Execution Order

Recommended order:
1. Finish the Gemini 3 Flash execution cost gate and choose the cheapest Gemini execution scaffold that does not materially degrade play
2. Run the cost-optimized hybrid planner championship on that fixed execution scaffold
3. Freeze the winner as a practical benchmark agent for later non-LLM engine evaluation
4. Run a planning-trace analysis pass on the saved observable model outputs to test whether Gemini’s edge is partly explained by stronger goal-directed objective tracking
5. Return to representation ablations or learning experiments only after the benchmark agent and planning story are no longer fragile

### Next-stage research question

The next article-grade question is no longer just “which provider wins?”.

It is:
- can a cheaper Gemini execution scaffold preserve most of the strong live-agent behavior?
- once execution is fixed to that cheaper scaffold, which providers add real value in the planning phase?
- does Gemini’s edge appear to come partly from more persistent, explicit objective tracking in its planning text?

The broader framing is a system-design question:
- when an LLM agent is decomposed into planning and execution layers, which model should do which job?
- when does a faster, cheaper operational model outperform a stronger but slower frontier model in the overall system?
- how much value comes from picking the right model for each subtask rather than from picking a single “best” model?

That last question should be studied from the saved observable planning outputs, not from hidden chain-of-thought. The right evidence is things like:
- explicit distance-to-target language
- repeated re-anchoring on the `65%` victory condition
- aggressive path selection toward the win target rather than local tactical chatter
- adaptive replanning after a blocked line or failed attack sequence

## What This Program Lets Us Claim

If these experiments are run cleanly, the project should be able to support claims like:
- whether newer OpenAI generations actually play better
- whether model size materially changes strategic performance
- whether extra reasoning budget helps or merely adds latency
- which live-turn-safe provider representative performs best under fixed rules
- how close a strong open or more openly deployable model appears to be to current or earlier closed-model generations across multiple provider lineages
- whether the best practical LLM agent comes from a hybrid system design rather than from a single frontier model
- whether splitting planning and execution across different models can improve both cost and performance
- how to choose an affordable benchmark agent for later automated engine evaluation

That is a strong and coherent first article program without requiring an unrealistic number of games.

## Planned Dissemination Shapes

The same core evidence should support multiple outputs, each aimed at a different audience.

### 1. Research-style source article

Purpose:
- serve as the canonical write-up of methods, experiments, results, and interpretation

Core framing:
- this started as a model-comparison study and evolved into a systems-design study
- the deeper result is not only “who wins Risk”
- it is also “how to build a stronger and cheaper agent by decomposing planning and execution”

### 2. LinkedIn newsletter (`~1500` words)

Purpose:
- convert the research result into a practical leadership piece for builders and technical decision-makers

Core framing:
- expensive frontier models are often not the best end-to-end system choice
- real agent systems benefit from task decomposition
- the best architecture may combine one model for planning and another for execution

### 3. Towards Data Science article

Purpose:
- focus on experimental design, benchmarking methodology, and deployable lessons

Core framing:
- why benchmark wins do not directly imply real-world agent quality
- why timing, fallback behavior, and cost matter
- how to evaluate models as components inside a system rather than as isolated chat endpoints

### 4. Short social and video outputs

Planned derivatives:
- three short LinkedIn posts built around distinct findings
- one YouTube manuscript built around the broader “how to choose and compose LLMs in an agent system” story

These shorter outputs should reuse the same core evidence rather than invent new claims.
