import pandas as pd
import os
from datetime import datetime
from typing import List



def create_game_folder(base_folder="game_results"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    game_name = "game__" + timestamp
    game_folder = os.path.join(base_folder, game_name)
    os.makedirs(game_folder, exist_ok=True)
    return game_folder


def save_game_state(game_state: 'GameState', game_folder: str, 
                    turn_number: int, game_round: int):
    save_state = game_state.territories_df.copy()

    save_state['Turn_Number'] = turn_number
    save_state['Game_Round'] = game_round
    filename = os.path.join(game_folder, f"game_state_turn_{turn_number}.csv")
    save_state.to_csv(filename, index=False)

def save_player_data(players: List['PlayerAgent'], game_folder: str,
                      turn_number: int, game_round: int):
    player_data = []
    for player in players:
        player_data.append({
            "Name": player.name,
            "Troops": player.troops,
            "Troop Placement Errors": player.troop_placement_errors,
            "Return Formatting Errors": player.return_formatting_errors,
            "Attack Errors": player.attack_errors,
            "Fortify Errors": player.fortify_errors,
            "Card Trade Errors": player.card_trade_errors,
            "Accumulated Turn Time": player.accumulated_turn_time
        })
    
    df = pd.DataFrame(player_data)
    df['Turn_Number'] = turn_number
    df['Game_Round'] = game_round
    filename = os.path.join(game_folder, f"player_data_turn_{turn_number}.csv")
    df.to_csv(filename, index=False)