# Experiment Configs

Tracked JSON rosters for named experiments live here.

Use these when you want an explicit, inspectable agent mix on disk instead of relying only on a preset name.

Example:

```bash
make run-experiment ARGS="--label demo --agent-specs-file configs/experiments/openai_mini_medium_vs_high.json --num-games 16 --turn-time-limit-seconds 300 --placement-time-limit-seconds 50"
```

Tracked cross-provider examples:
- `2026_q2_cross_provider_frontier.json`: frozen standard live-turn frontier roster
- `2026_q2_cross_provider_frontier_strategic_smoke.json`: frozen strategic smoke roster with split planning overrides
