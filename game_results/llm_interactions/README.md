# LLM Interaction Logs

Runtime prompt/response logs are written here during live games and leagues.

Tracked in git:
- this folder
- `.gitkeep`
- this README

Ignored by git:
- per-game runtime logs under `game_results/llm_interactions/game__...`

Runtime hierarchy:
- `game_results/llm_interactions/<game_name>/<player>/round_<NN>/<scope or turn>/`

Examples:
- `game_results/llm_interactions/game__2026-04-26_21-00-00/gpt-5.4/round_00/initial_setup/0001_initial_troop_placement.json`
- `game_results/llm_interactions/game__2026-04-26_21-00-00/gpt-5.4/round_03/turn_0010/0004_attack.json`

Each JSON file contains:
- provider and model metadata
- full prompt text
- raw model response
- timeout and reasoning settings used for the call
- fallback status
- raw provider error text when a call fails
