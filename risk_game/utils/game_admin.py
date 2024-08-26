import pandas as pd
import os
from datetime import datetime
from typing import List, Optional
import json



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

def save_end_game_results(players: List["PlayerAgent"], winner: Optional[str], 
                          victory_condition: Optional[str], game_round: int, 
                          games_folder: str, game_state: 'GameState') -> None:
    """
    Save the end game results to a JSON file.

    Parameters:
    - players: List of PlayerAgent instances representing the players.
    - winner: The name of the winning player (or None if no winner).
    - victory_condition: The victory condition met (or None if no specific condition).
    - game_round: The number of rounds the game lasted.
    - games_folder: The folder where the results should be saved.
    """

    # Prepare the file path
    end_game_file = os.path.join(games_folder, 'end_game_results.json')
    
    # Gather player data
    player_data = []
    for player in players:
        player_data.append({
            'name': player.name,
            'total_troops': player.troops,
            'territories_controlled': len(game_state.get_player_territories(player.name)),
            'troop_placement_errors': player.troop_placement_errors,
            'return_formatting_errors': player.return_formatting_errors,
            'attack_errors': player.attack_errors,
            'fortify_errors': player.fortify_errors,
            'card_trade_errors': player.card_trade_errors
        })
    
    # Prepare the end-game data
    end_game_data = {
        'winner': winner if winner else 'No Winner',
        'victory_condition': victory_condition if victory_condition else 'None',
        'total_rounds': game_round,
        'players': player_data
    }
    
    # Write the data to a JSON file
    with open(end_game_file, 'w') as file:
        json.dump(end_game_data, file, indent=4)