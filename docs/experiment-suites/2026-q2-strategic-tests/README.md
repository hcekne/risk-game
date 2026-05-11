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
- primary endpoint: win count / win rate under the configured territory-control victory rule
- secondary endpoints: final territory share, survival, fallback rate, invalid move rate, strategic rubric score, turn time, tracked token usage, and estimated API cost

Preferred statistical approach:
- winner-label permutation test for the primary omnibus comparison
- exact binomial or sign-style tests for post-hoc pairwise winner comparisons
- Holm correction across post-hoc pairwise tests
- blocked permutation on final territory totals as a secondary descriptive strength check where useful

Why this protocol:
- each game contains all compared agents
- seat rotation balances player-order effects
- the models are explicitly asked to win by reaching the game victory condition
- win-based tests therefore match the optimization target the agents actually see

Historical note:
- some older tracked notes still analyze final territory share as the primary endpoint because they predate the win-first policy update on `2026-05-04`
- current and future tracked analyses should treat wins as primary and territory totals as secondary

## Cost Estimation Method

For post-instrumentation experiments, estimated API cost is computed from saved per-call usage metadata plus a local pricing snapshot.

Method:
- the runtime logs provider/model/client-role metadata and token usage for each LLM call
- the summary pipeline aggregates input, cached-input, output, and reported reasoning tokens per player
- estimated cost is computed with the pricing table in [risk_game/utils/model_pricing.py](../../../risk_game/utils/model_pricing.py)

Current formula:
- `uncached_input_tokens / 1_000_000 * input_usd_per_million_tokens`
- `cached_input_tokens / 1_000_000 * cached_input_usd_per_million_tokens`
- `output_tokens / 1_000_000 * output_usd_per_million_tokens`
- summed across all calls for the player or experiment

Important caveats:
- these are **estimated** costs, not provider billing exports
- they depend on the local pricing snapshot ID recorded in the summary
- old experiments run before usage logging was added cannot be backfilled reliably and should show `0` or `null` cost fields
- reasoning tokens are tracked separately where providers expose them, but they are not priced separately unless the pricing table explicitly models a distinct billed dimension

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
| Complete | OpenAI Generation Ladder Strategic 32 | Under `90s` isolated planning plus `90s / 15s` live execution, which full-stack OpenAI generation is the strongest practical Risk agent: `gpt-5.4`, `gpt-5.2`, `gpt-5.1`, or `gpt-4.1`? | `/shared-game-results/experiments/experiment__2026-05-02_09-00-55__openai_generation_ladder_541_strategic_16`<br>`/shared-game-results/experiments/experiment__2026-05-03_07-17-54__openai_generation_ladder_541_strategic_16_rep2` | [2026-05-04_openai-generation-ladder-541-strategic-32.md](2026-05-04_openai-generation-ladder-541-strategic-32.md) |
| Complete | OpenAI 5.1 Execution Hybrid Planning Showdown | If execution is fixed at `gpt-5.1`, do `gpt-5.2`, `gpt-5.4`, or `gpt-5.5` produce a clearly better planning signal than `gpt-5.1` itself? | `/shared-game-results/experiments/experiment__2026-05-03_20-35-06__openai_51_execution_hybrid_planning_showdown_16` | [2026-05-04_openai-51-execution-hybrid-planning-showdown.md](2026-05-04_openai-51-execution-hybrid-planning-showdown.md) |
| Planned | OpenAI Mini High-Strategic Hybrid | Does `high` help when reserved for planning/attack only, while faster settings handle administrative phases? | pending | [2026-04-29_openai-mini-high-strategic-hybrid-plan.md](2026-04-29_openai-mini-high-strategic-hybrid-plan.md) |
| Deferred | Historical OpenAI Generation Ladder | The earlier `gpt-5.5` vs `gpt-5.4` vs `gpt-4.1` plan has been superseded by the completed strategic `32`-game OpenAI generation result. | superseded by `/shared-game-results/experiments/experiment__2026-05-02_09-00-55__openai_generation_ladder_541_strategic_16` and `/shared-game-results/experiments/experiment__2026-05-03_07-17-54__openai_generation_ladder_541_strategic_16_rep2` | [2026-05-04_openai-generation-ladder-541-strategic-32.md](2026-05-04_openai-generation-ladder-541-strategic-32.md) |
| Planned | OpenAI Size Ladder | `gpt-5.4` vs `gpt-5.4-mini` vs `gpt-5.4-nano` | pending | pending |
| Blocked | Cross-Provider Frontier Strategic Full 16 | Can the new strategic frontier condition complete a research-sized `16`-game batch? | `/shared-game-results/experiments/experiment__2026-05-01_21-52-42__frontier_strategic_full_16` | blocked at launch by Gemini daily quota exhaustion; see [2026-05-02_cross-provider-frontier-strategic-smoke.md](2026-05-02_cross-provider-frontier-strategic-smoke.md) |
| Invalid | Cross-Provider Frontier Strategic Full 16 Retry 1 | Does the updated strategic cross-provider roster produce a valid `16`-game provider comparison under `90 / 90 / 15` timing? | `/shared-game-results/experiments/experiment__2026-05-04_11-33-15__frontier_strategic_full_16` | [2026-05-04_cross-provider-frontier-strategic-full-invalid.md](2026-05-04_cross-provider-frontier-strategic-full-invalid.md) |
| Partial | Cross-Provider Frontier Strategic Full 16 Retry 2 | Can the Anthropic-credit-contaminated rerun be salvaged by keeping the clean games and topping up the missing seat rotations? | `/shared-game-results/experiments/experiment__2026-05-04_21-00-11__frontier_strategic_full_16_retry_2` | [2026-05-05_cross-provider-frontier-strategic-retry-2-salvage-plan.md](2026-05-05_cross-provider-frontier-strategic-retry-2-salvage-plan.md) |
| Complete | Cross-Provider Frontier Strategic 16 Salvaged | After dropping Anthropic-credit-contaminated retry-2 games and appending a clean 6-game seat-balance top-up, which provider leads the balanced `16`-game strategic frontier batch? | `/shared-game-results/experiment_series/frontier_strategic_full_16_salvaged` | [2026-05-06_cross-provider-frontier-strategic-16-salvaged.md](2026-05-06_cross-provider-frontier-strategic-16-salvaged.md) |
| Complete | Cross-Provider Strategic Replicate 2 | Does Gemini's lead survive a second clean balanced `16`-game replicate of the same frozen strategic provider roster? | `/shared-game-results/experiments/experiment__2026-05-06_11-13-05__frontier_strategic_replicate_2_16` | [2026-05-07_cross-provider-frontier-strategic-replicate-2.md](2026-05-07_cross-provider-frontier-strategic-replicate-2.md) |
| Complete | Cross-Provider Strategic 32 Pooled | If the balanced salvaged `16` and the clean direct `16` were run under the same exact frozen condition, what is the best current pooled estimate of provider strength? | `/shared-game-results/experiment_series/frontier_strategic_provider_32_pooled` | [2026-05-07_cross-provider-frontier-strategic-32-pooled.md](2026-05-07_cross-provider-frontier-strategic-32-pooled.md) |
| Complete | Kimi Capability Anchoring: OpenAI Team Arena | In a duplicate-team `2x2` setup, is `kimi-k2.6` closer to the current OpenAI live baseline or to an earlier GPT tier under the same live strategic condition? | `/shared-game-results/experiments/experiment__2026-05-07_15-34-43__kimi_anchor_openai_gpt41_team_16` | [2026-05-08_kimi-anchor-openai-gpt41-team.md](2026-05-08_kimi-anchor-openai-gpt41-team.md) |
| Complete | Kimi Capability Anchoring: Gemini Team Arena | In a duplicate-team `2x2` setup, does `kimi-k2.6` look broadly competitive with an older Gemini anchor tier, or does `gemini-2.5-pro` still hold a real edge under the same live strategic condition? | `/shared-game-results/experiments/experiment__2026-05-07_15-35-19__kimi_anchor_gemini25pro_team_16` | [2026-05-08_kimi-anchor-gemini25pro-team.md](2026-05-08_kimi-anchor-gemini25pro-team.md) |
| Complete | Kimi Capability Anchoring: Anthropic Sonnet Team Arena | In a duplicate-team `2x2` setup, does `kimi-k2.6` remain broadly competitive with an older Anthropic Sonnet anchor under the same live strategic condition? | `/shared-game-results/experiments/experiment__2026-05-07_17-43-42__kimi_anchor_anthropic_sonnet4_20250514_team_16` | [2026-05-08_kimi-anchor-anthropic-sonnet4-team.md](2026-05-08_kimi-anchor-anthropic-sonnet4-team.md) |
| Archived | Kimi Capability Anchoring: Anthropic Sonnet 4.5 Follow-up | The Sonnet 4.5 team run completed, but it is not part of the main anchoring story because the runtime mismatch is too severe and the pricing table is incomplete for this model. | `/shared-game-results/experiments/experiment__2026-05-07_17-43-31__kimi_anchor_anthropic_sonnet45_team_16` | [2026-05-08_kimi-anchor-anthropic-sonnet45-archived.md](2026-05-08_kimi-anchor-anthropic-sonnet45-archived.md) |
| Complete | Gemini 3 Flash Execution Cost Gate | Can `gemini-3-flash-preview` serve as the cheap live execution scaffold, and is `gemini-3.1-pro-preview` planning on Flash execution the best practical Gemini value point? | `/shared-game-results/experiment_series/gemini3_flash_execution_cost_gate_15_pooled` | [2026-05-09_gemini3-flash-execution-cost-gate.md](2026-05-09_gemini3-flash-execution-cost-gate.md) |
| Complete | Gemini 3 Flash Execution Planner Hybrid Bakeoff 32 | Once execution is fixed to `gemini-3-flash-preview`, do the provider planning models still separate clearly, or does most of the spread collapse? | `/shared-game-results/experiment_series/gemini3_flash_execution_planner_hybrid_bakeoff_32_pooled` | [2026-05-09_gemini3-flash-execution-planner-hybrid-bakeoff-32.md](2026-05-09_gemini3-flash-execution-planner-hybrid-bakeoff-32.md) |
| Complete | Claude vs Kimi Flash-Exec Planner Team Duel | If the four-way Flash-exec planner bakeoff suggests only a weak Claude-over-Kimi edge, does a direct duplicate-team duel separate them more clearly? | `/shared-game-results/experiment_series/claude_vs_kimi_flash_exec_planner_team_16_pooled` | [2026-05-10_claude-vs-kimi-flash-exec-planner-team.md](2026-05-10_claude-vs-kimi-flash-exec-planner-team.md) |

Shared artifact audit on `2026-05-02`:
- completed shared batches currently present: `mini_reasoning_2`, `mini_medium_vs_high_300s_16`, `frontier_smoke`, and `frontier_strategic_smoke`
- no shared completed batches were found for `openai_generation_ladder`, `openai_size_ladder`, or `openai_mini_high_strategic_hybrid`

Update on `2026-05-04`:
- the shared store now also contains the completed strategic generation-ladder replicates:
  - `openai_generation_ladder_541_strategic_16`
  - `openai_generation_ladder_541_strategic_16_rep2`
- the combined tracked conclusion is that `gpt-5.1` is the strongest current working full-stack OpenAI live-turn baseline under the strategic `90 / 90 / 15` condition
- under the narrower `gpt-5.1`-vs-rest follow-up family, the combined `32` games support `gpt-5.1 > gpt-5.2` on wins
- under the broader all-pairs family across all `6` unordered comparisons, that `gpt-5.1 > gpt-5.2` claim remains short of Holm correction
- the later `openai_51_execution_hybrid_planning_showdown_16` batch is much more even and does **not** establish a planning winner; a skeptic can plausibly explain the `5 / 4 / 4 / 3` win split by chance
- the `2026-05-04` strategic cross-provider retry is invalid because of a setup parser bug plus later OpenAI quota exhaustion; it should be rerun from scratch
- the `2026-05-04 21:00 UTC` strategic cross-provider rerun completed, but Anthropic low-credit failures contaminate games `7-12`; keep games `1-6` and `13-16`, then append the planned `frontier_strategic_topup_6` batch to restore a clean balanced `16`-game provider set
- the completed top-up batch did run clean, and the reconstructed balanced `16`-game provider series now favors `gemini-3.1-pro-preview` clearly over Claude, GPT-5.1, and Kimi
- that Gemini-led result shifts the next priority from more OpenAI-only ladder cleanup to one clean confirmatory provider replicate; provider-failure pause/resume handling is now in place
- the confirmatory provider replicate is now complete and again gives Gemini `10 / 16` wins
- pooling the balanced salvaged `16` plus the clean direct `16` yields a `32`-game provider result of Gemini `20`, GPT-5.1 `6`, Claude `4`, Kimi `2`
- the next scored stage is no longer provider replication; it is Kimi capability anchoring against older OpenAI, Gemini, and Anthropic team arenas under the same frozen live strategic condition
- the first completed Kimi capability anchor against duplicated `gpt-4.1` shows a narrow `9-7` OpenAI edge that is fully compatible with chance, while Kimi remains materially cheaper on estimated API cost
- the first completed Kimi capability anchor against duplicated `gemini-2.5-pro` shows a narrow `9-7` Gemini edge; that is directionally stronger than the GPT-4.1 anchor result, but still not a large gap on wins alone
- the first completed Kimi capability anchor against duplicated `claude-sonnet-4-20250514` shows a narrow `9-7` Kimi edge that is fully compatible with chance, but Kimi is vastly cheaper and materially cleaner on timeout behavior
- the attempted Sonnet 4.5 follow-up is archived from the main story because the runtime mismatch is too severe and pricing support for that model is missing
- taken together, the current Kimi anchor picture is: roughly GPT-4.1-class, somewhat below Gemini 2.5 Pro, competitive with this older Anthropic Sonnet tier, and far below the current pooled Gemini 3.1 provider lead
- a useful public framing is that Kimi 2.6 arrives roughly `10-13` months after Gemini 2.5 Pro depending on whether one counts the first public experimental release or the later GA release, yet still does not clearly surpass that older Gemini tier in this live strategic environment
- the pooled Gemini 3 Flash cost gate supports a practical scaffold change: keep `gemini-3.1-pro-preview` for planning and move all non-planning phases to `gemini-3-flash-preview`
- the pooled `32`-game Flash-exec planner bakeoff does **not** crown a clear planning winner; instead it shows that once execution is standardized to cheap Gemini Flash, most of the provider spread compresses into a near-equal planning band
- the direct duplicate-team Claude-vs-Kimi planner duel also stays near parity at `9-7`; Claude is cleaner on secondary metrics, but the win gap is still fully compatible with chance

## Analyst Notes

The suite is designed so future analysts can add new experiments without rewriting the whole repo narrative.

When adding a new experiment:
1. run the batch and keep the raw output under the runtime `game_results/experiments/...` root
2. write a tracked Markdown note in this folder
3. update the registry table above
4. if the experiment changes methodology, document that explicitly rather than silently changing assumptions

## Supplemental Analyses

These notes do not introduce new game batches. They extract mechanism-level findings from already completed series.

- [2026-05-10_provider32-goal-directedness-trace-analysis.md](2026-05-10_provider32-goal-directedness-trace-analysis.md)
- [2026-05-10_provider32-execution-trace-analysis.md](2026-05-10_provider32-execution-trace-analysis.md)
