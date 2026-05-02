# 2026-Q2 Strategic Tests

This suite is the main tracked experiment program for the 2026 Q2 round of Risk-based strategic capability testing.

Scope:
- GPT-5.x generation models and variants
- top closed-model competitors
- top open-model competitors
- reasoning-mode and model-size comparisons
- strategic performance under synchronous live-turn constraints

This suite complements [docs/experiment-program.md](../experiment-program.md), which defines the broader planned program. The suite folder records what has actually been run and what the results mean.

For a machine-level inventory of completed experiments and generated outputs, plus the Dropbox handoff plan for moving those artifacts between machines, see [docs/artifact-storage-and-dropbox-sync.md](../../artifact-storage-and-dropbox-sync.md).

## Common Protocol

Unless an experiment note says otherwise, use these defaults:
- seat rotation enabled
- fixed prompts and parser/output grammar
- deterministic engine version recorded in `game_manifest.json`
- primary endpoint: final territory share
- secondary endpoints: win count, survival, fallback rate, invalid move rate, strategic rubric score, turn time

Preferred statistical approach:
- blocked permutation test for the primary omnibus comparison
- blocked pairwise permutation tests for post-hoc comparisons
- Holm correction across post-hoc pairwise tests
- exact binomial or sign-style supporting tests where useful

Why this protocol:
- each game contains all compared agents
- seat rotation balances player-order effects
- nonparametric blocked tests fit the design without strong distributional assumptions

## Raw Artifact Convention

Tracked suite notes live here in `docs/experiment-suites/...`.

Raw runtime artifacts live under the `game_results` root, usually:
```text
/shared-game-results/experiments/experiment__YYYY-MM-DD_HH-MM-SS__label
```

Those folders are intentionally git-ignored. The tracked analysis note should always include the exact local artifact path it refers to.

## Experiment Registry

| Status | Experiment | Question | Raw Artifacts | Tracked Analysis |
| --- | --- | --- | --- | --- |
| Complete | OpenAI Mini Reasoning 2 | In a constrained synchronous live-turn environment, does `gpt-5.4-mini` perform differently at `none/low/medium/high` reasoning levels? | `/shared-game-results/experiments/experiment__2026-04-27_22-29-27__mini_reasoning_2` | [2026-04-27_openai-mini-reasoning.md](2026-04-27_openai-mini-reasoning.md) |
| Complete | OpenAI Mini High-vs-Medium Recovery | If `high` is given more time, does it recover against `medium`? | `/shared-game-results/experiments/experiment__2026-04-28_14-57-43__mini_medium_vs_high_300s_16` | [2026-04-29_openai-mini-high-vs-medium-recovery.md](2026-04-29_openai-mini-high-vs-medium-recovery.md) |
| Complete | Cross-Provider Frontier Smoke 1 | Does the locked cross-provider frontier roster complete a clean live-turn smoke game under shared timers and prompts? | `/shared-game-results/experiments/experiment__2026-04-29_20-44-02__frontier_championship_smoke_1` | local artifact only; detailed suite note pending |
| Complete | Cross-Provider Frontier Smoke 2 | Under the standard `90s / 15s` live-turn policy, which frontier candidates remain operationally clean and which ones time out often enough to warrant roster changes? | `/shared-game-results/experiments/experiment__2026-05-01_09-03-34__frontier_smoke` | [2026-05-01_cross-provider-frontier-smoke.md](2026-05-01_cross-provider-frontier-smoke.md) |
| Complete | Cross-Provider Frontier Strategic Smoke | Under the earlier `60s` isolated-planning strategic condition, do the frontier candidates remain operationally usable? | `/shared-game-results/experiments/experiment__2026-05-01_20-51-42__frontier_strategic_smoke` | [2026-05-02_cross-provider-frontier-strategic-smoke.md](2026-05-02_cross-provider-frontier-strategic-smoke.md) |
| Planned | OpenAI Mini High-Strategic Hybrid | Does `high` help when reserved for planning/attack only, while faster settings handle administrative phases? | pending | [2026-04-29_openai-mini-high-strategic-hybrid-plan.md](2026-04-29_openai-mini-high-strategic-hybrid-plan.md) |
| Planned | OpenAI Generation Ladder | `gpt-5.5` vs `gpt-5.4` vs `gpt-4.1` | pending | pending |
| Planned | OpenAI Size Ladder | `gpt-5.4` vs `gpt-5.4-mini` vs `gpt-5.4-nano` | pending | pending |
| Blocked | Cross-Provider Frontier Strategic Full 16 | Can the new strategic frontier condition complete a research-sized `16`-game batch? | `/shared-game-results/experiments/experiment__2026-05-01_21-52-42__frontier_strategic_full_16` | blocked at launch by Gemini daily quota exhaustion; see [2026-05-02_cross-provider-frontier-strategic-smoke.md](2026-05-02_cross-provider-frontier-strategic-smoke.md) |
| Planned | Cross-Provider Championship | best live-turn-safe OpenAI vs Anthropic vs Gemini vs Kimi | pending | pending |
| Planned | Open-vs-Closed Capability Anchoring | place Kimi against historical GPT tiers | pending | pending |

Shared artifact audit on `2026-05-02`:
- completed shared batches currently present: `mini_reasoning_2`, `mini_medium_vs_high_300s_16`, `frontier_smoke`, and `frontier_strategic_smoke`
- no shared completed batches were found for `openai_generation_ladder`, `openai_size_ladder`, or `openai_mini_high_strategic_hybrid`

## Analyst Notes

The suite is designed so future analysts can add new experiments without rewriting the whole repo narrative.

When adding a new experiment:
1. run the batch and keep the raw output under the runtime `game_results/experiments/...` root
2. write a tracked Markdown note in this folder
3. update the registry table above
4. if the experiment changes methodology, document that explicitly rather than silently changing assumptions
