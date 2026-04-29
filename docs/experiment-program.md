# Experiment Program

This document defines the first serious experiment program for the Risk project.

It is designed to answer a small number of high-value questions under realistic budget and time constraints, while still producing results that are defensible enough to use in a follow-up article.

For completed tracked write-ups from this program, use the suite archive under [docs/experiment-suites/README.md](experiment-suites/README.md).

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

For this reason, the Kimi track should not stop at “does it beat today’s closed leaders?” If needed, it should also try to locate Kimi relative to earlier GPT generations.

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
- final territory share

Secondary endpoints:
- win rate
- finish rank
- survival length
- invalid move rate
- fallback rate
- mean turn time
- strategic rubric score

### Statistical approach

For each experiment:
- Pre-register one primary outcome: final territory share.
- Use one omnibus null hypothesis first.
- Then use planned pairwise comparisons on final territory share.
- Treat win rate and rubric as supporting evidence, not the sole headline metric.
- Report effect sizes and confidence intervals, not only p-values.

Recommended analysis methods:
- blocked permutation test on final territory share
- bootstrap confidence intervals for pairwise differences

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
- H0: mean final territory share is equal across `gpt-5.5`, `gpt-5.4`, and `gpt-4.1`

Primary alternative hypothesis:
- H1: at least one model has a different mean final territory share

Planned directional expectation:
- `gpt-5.5 > gpt-5.4 > gpt-4.1`

Why this experiment matters:
- It answers the cleanest public question: does a newer model generation actually produce stronger strategic play?

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
- H0: mean final territory share is equal across the GPT-5.4 size variants

Primary alternative hypothesis:
- H1: at least one size variant has a different mean final territory share

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
- H0: mean final territory share is equal across the three reasoning settings

Primary alternative hypothesis:
- H1: at least one reasoning setting has a different mean final territory share

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
- OpenAI: `gpt-5.5`
- Anthropic: `claude-opus-4-7` in standard mode by default; adaptive thinking is now viable too, but should be treated as a separate condition rather than silently turned on
- Google: `gemini-3.1-pro-preview` as the chosen Google representative
- Moonshot: `kimi-k2.6` with thinking disabled

Design:
- `4` players
- `16` games
- no learning between games
- every candidate must pass a smoke test before entering the full championship

Primary null hypothesis:
- H0: mean final territory share is equal across the provider representatives

Primary alternative hypothesis:
- H1: at least one provider representative has a different mean final territory share

Directional expectation:
- no directional ordering should be pre-registered here

Why this experiment matters:
- This is the main “who is strongest right now in usable live play?” experiment.

Important constraint:
- This is a **usable live-turn** championship, not a “best model in the abstract” championship.
- A model that is too slow, too unstable, or too format-fragile to function as a synchronous player should be excluded on methodological grounds.
- For this reason, `kimi-k2.6` should only enter with thinking disabled, and `gpt-5.5-pro` remains excluded from synchronous live-turn play.

## Experiment 5: Open-vs-Closed Capability Anchoring

Question:
- If `kimi-k2.6` is not clearly the strongest in the cross-provider field, where does it sit relative to earlier OpenAI model generations?

Core idea:
- The cross-provider championship tells us whether Kimi is competitive with the current closed frontier.
- This fifth experiment tells us how to interpret the result if it is not.
- It is an anchoring experiment: it tries to locate Kimi on a rough strategic-capability timeline.

When to run it:
- run this after Experiment 4
- prioritize it if `kimi-k2.6` is clearly weaker than the best closed models but still appears competent and live-turn viable
- if `kimi-k2.6` wins or ties for the top in Experiment 4, this experiment becomes optional rather than mandatory

Provisional lineup:
- `kimi-k2.6`
- `gpt-5.4`
- `gpt-4.1`

Possible extension lineup:
- replace `gpt-5.4` with a weaker historical anchor such as `gpt-4o` if the first anchor run suggests Kimi is closer to that tier than to `gpt-5.4`

Design:
- `3` players
- `15` games
- no learning between games

Primary null hypothesis:
- H0: mean final territory share is equal across `kimi-k2.6`, `gpt-5.4`, and `gpt-4.1`

Primary alternative hypothesis:
- H1: at least one model has a different mean final territory share

Interpretive goal:
- not just “did Kimi win?”
- instead: does Kimi look closer to the current closed frontier, the previous closed generation, or below that?

Why this experiment matters:
- It is the clearest way to translate a cross-provider result into a statement people will actually care about.
- It supports the sovereign-AI question directly by estimating how much strategic capability can currently be accessed outside the most closed frontier systems.
- It produces a more nuanced conclusion than a simple provider leaderboard.

Important note:
- This experiment is especially valuable for article-writing because it lets us say things like:
  - `kimi-k2.6` looked competitive with `gpt-4.1` but not with `gpt-5.4`
  - or `kimi-k2.6` played at roughly current-closed-frontier level under these game conditions
- Those are much more interpretable public claims than “Kimi finished second in one tournament.”

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
- final territory share by game
- win rate by model
- mean and median finish rank
- invalid move rate
- fallback rate
- mean turn time
- strategic rubric average
- pairwise effect sizes on final territory share

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
1. Finish provider smoke tests for Anthropic, Gemini, and Kimi
2. Run Experiment 1: Generation Ladder
3. Run Experiment 2: Size Ladder
4. Run Experiment 3: Reasoning-Budget Ladder
5. Run Experiment 4: Cross-Provider Live-Turn Championship
6. Run Experiment 5: Open-vs-Closed Capability Anchoring if Kimi remains live-turn viable

## What This Program Lets Us Claim

If these experiments are run cleanly, the project should be able to support claims like:
- whether newer OpenAI generations actually play better
- whether model size materially changes strategic performance
- whether extra reasoning budget helps or merely adds latency
- which live-turn-safe provider representative performs best under fixed rules
- how close a strong open-weight or more openly deployable model appears to be to current or earlier closed-model generations

That is a strong and coherent first article program without requiring an unrealistic number of games.
