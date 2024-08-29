# Example 1

from risk_game.experiments import Experiment
from risk_game.game_config import GameConfig

# Correct: Creating an instance of GameConfig
config = GameConfig(progressive=True, capitals=False, max_rounds=17)


# Run a single game with default options
experiment = Experiment(config, agent_mix=1, num_games=2)
experiment

print(experiment)


experiment.run_experiment()











# #################
# # Example 2

# from risk_game.rules import Rules
# from risk_game.game_config import GameConfig
# from risk_game.game_master import GameMaster as gm
# from risk_game.llm_clients import llm_client

# # Correct: Creating an instance of GameConfig
# config = GameConfig(progressive=True, capitals=False, max_rounds=2)

# # Correct: Creating an instance of Rules
# rules = Rules(config)

# rules

# g1 = gm(rules)

# g1.add_player(name="llama3.1_70b_AWS", 
#                         llm_client=llm_client.create_llm_client("Bedrock", 2))

# g1.players[0].send_message("Can you help me play risk? I'm new to this game.")

# # g1.add_player(name="Test Player 1", 
# #                         llm_client=llm_client.create_llm_client("Groq", 2))
# # g1.add_player(name="Test Player 2", 
# #             llm_client=llm_client.create_llm_client("OpenAI", 2))
# # g1.add_player(name="Test Player 3", 
# #             llm_client=llm_client.create_llm_client("OpenAI", 2))

# print(g1.players[0])

# g1

# g1.play_game()


