import risk_game.game_master as gm
import risk_game.card_deck as cd
from risk_game.rules import Rules
import pandas as pd
from risk_game.llm_clients import llm_client
import importlib
from risk_game.utils.game_admin import create_game_folder



### PHASE 0: Initialize the game

# Initialize the rules
rules = Rules(progressive=False, capitals=False, mode="world_domination",
                max_rounds=2)

game = gm.GameMaster(rules)

game.add_player(name="Player_Player 1", 
                llm_client=llm_client.create_llm_client("Groq",1 ))


game.add_player(name="Player_Player 2",
                llm_client=llm_client.create_llm_client("Anthropic",1 ))


game.add_player(name="Player_Player 4", 
                llm_client=llm_client.create_llm_client("OpenAI",1 ))

print(game.players)  # This should now show PlayerAgent objects



games_folder = create_game_folder(base_folder="game_results")


game.play_game(include_initial_troop_placement=False)

print(game.game_state.territories_df)