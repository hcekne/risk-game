# Experiment Configs

Tracked JSON rosters for named experiments live here.

Use these when you want an explicit, inspectable agent mix on disk instead of relying only on a preset name.

Example:

```bash
make run-experiment ARGS="--label demo --agent-specs-file configs/experiments/openai_mini_medium_vs_high.json --num-games 16 --turn-time-limit-seconds 300 --placement-time-limit-seconds 50"
```
