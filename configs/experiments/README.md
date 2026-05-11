# Experiment Configs

Tracked JSON rosters for named experiments live here.

Use these when you want an explicit, inspectable agent mix on disk instead of relying only on a preset name.

Example:

```bash
make run-experiment ARGS="--label demo --agent-specs-file configs/experiments/openai_mini_medium_vs_high.json --num-games 16 --turn-time-limit-seconds 300 --placement-time-limit-seconds 50"
```

Tracked cross-provider examples:
- `2026_q2_cross_provider_frontier.json`: frozen standard live-turn frontier roster
- `2026_q2_cross_provider_frontier_strategic.json`: current strategic cross-provider roster with `gpt-5.1` execution and `gpt-5.5` planning for OpenAI
- `2026_q2_cross_provider_frontier_strategic_smoke.json`: frozen strategic smoke roster with split planning overrides
- `2026_q2_kimi_anchor_openai_gpt41_team.json`: duplicate-team `2x kimi-k2.6` vs `2x gpt-4.1` anchor arena
- `2026_q2_kimi_anchor_gemini25pro_team.json`: duplicate-team `2x kimi-k2.6` vs `2x gemini-2.5-pro` anchor arena
- `2026_q2_kimi_anchor_anthropic_opus4_20250514_team.json`: duplicate-team `2x kimi-k2.6` vs `2x claude-opus-4-20250514` anchor arena
- `2026_q2_kimi_anchor_anthropic_sonnet45_team.json`: duplicate-team `2x kimi-k2.6` vs `2x claude-sonnet-4-5-20250929` anchor arena
- `2026_q2_kimi_anchor_anthropic_sonnet4_20250514_team.json`: duplicate-team `2x kimi-k2.6` vs `2x claude-sonnet-4-20250514` anchor arena
- `2026_q2_gemini_execution_planner_bakeoff.json`: `gemini-3.1-pro-preview` full baseline versus `gpt-5.5`, `claude-opus-4-7`, and `kimi-k2.6` as planning-only overrides on Gemini execution
- `2026_q2_gemini3_flash_execution_cost_gate.json`: `gemini-3.1-pro-preview` full vs `gemini-3-flash-preview` full vs `gemini-3.1-pro-preview` planning on `gemini-3-flash-preview` execution
- `2026_q2_gemini3_flash_execution_planner_hybrid_bakeoff.json`: four-provider planning-only bakeoff with `gemini-3-flash-preview` handling all non-planning phases
- `2026_q2_claude_vs_kimi_flash_exec_planner_team.json`: duplicate-team `2x claude-opus-4-7` planner vs `2x kimi-k2.6` planner with shared `gemini-3-flash-preview` execution

Tracked OpenAI-only examples:
- `openai_generation_ladder_strategic.json`: `gpt-5.5` vs `gpt-5.4` vs `gpt-4.1` under isolated `90s` planning plus `90s / 15s` live execution
- `openai_generation_ladder_541_strategic.json`: `gpt-5.4` vs `gpt-5.2` vs `gpt-5.1` vs `gpt-4.1` under isolated `90s` planning plus `90s / 15s` live execution
- `openai_51_execution_hybrid_planning_showdown.json`: `gpt-5.1` full-stack baseline vs `gpt-5.5`, `gpt-5.4`, and `gpt-5.2` planning-only overrides with `gpt-5.1` execution
