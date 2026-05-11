# Kimi vs Anthropic Sonnet 4.5 Team Arena Archived

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `kimi_anchor_anthropic_sonnet45_team_16`
- Raw artifacts: `/shared-game-results/experiments/experiment__2026-05-07_17-43-31__kimi_anchor_anthropic_sonnet45_team_16`
- Status: archived / not used in the main Kimi anchoring story

## Reason For Archival

This run is not being kept as a main-line anchor result.

The problem is not that the experiment crashed. It completed. The problem is that it is a poor fit for the question we actually care about.

Why it is being archived:

1. **It adds little beyond the Sonnet 4 (20250514) anchor.**
   - The older Sonnet 4 anchor already shows that Kimi is broadly competitive with an older Anthropic tier.
   - That is enough for the current cross-family anchoring story.

2. **The runtime mismatch is too severe.**
   - `claude-sonnet-4-5-20250929` posted extremely high fallback and timeout rates under this live harness.
   - In this run, each Claude copy averaged about `24.5-25.5` fallback calls and about `10.6-10.8` timed-out turns per game.
   - That makes the result much more about deployment mismatch than about clean strategic comparison.

3. **The cost analysis is incomplete.**
   - The pricing table does not yet include `Anthropic:claude-sonnet-4-5-20250929`.
   - The summary therefore records missing pricing and `0.0` estimated Claude cost.
   - That makes this run unusable for one of the repo’s now-important secondary dimensions: cost-adjusted performance.

4. **The win result is not needed to support the current article claim.**
   - Kimi won `11 / 16`, but at this sample size the win gap is still not decisive on exact binomial testing.
   - More importantly, the more interpretable anchor story is already:
     - near `gpt-4.1`
     - somewhat below `gemini-2.5-pro`
     - competitive with `claude-sonnet-4-20250514`

## Practical Interpretation

This run still taught us something useful:
- `claude-sonnet-4-5-20250929` is a poor candidate for this particular live strategic anchoring program under the current thinking-enabled full-stack harness

Most likely reasons:
- manual-thinking-only Anthropic path
- high verbosity / long outputs
- too much wall-clock spent inside the live turn loop
- severe timeout pressure during placement and execution phases

So the right policy is:
- do **not** use Sonnet 4.5 as a main Anthropic anchor in this story
- use the older Sonnet 4 anchor instead
- revisit Sonnet 4.5 only if the Anthropic execution harness is redesigned specifically for it
