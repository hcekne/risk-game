# Example: run a short GPT-5.4 mini reasoning arena.

from risk_game.experiments import Experiment, build_openai_mini_reasoning_arena
from risk_game.game_config import GameConfig

config = GameConfig(
    progressive=True,
    capitals=False,
    max_rounds=10,
    turn_time_limit_seconds=120,
    placement_time_limit_seconds=25,
)

experiment = Experiment(
    config,
    num_games=2,
    agent_specs=build_openai_mini_reasoning_arena(),
)

print(experiment)
experiment.run_experiment()
