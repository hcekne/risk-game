import json
import os
import subprocess
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

import pandas as pd

from risk_game.paths import get_game_results_dir



def create_game_folder(base_folder: str | None = None):
    if base_folder is None:
        base_folder = str(get_game_results_dir())
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    game_name = "game__" + timestamp
    game_folder = os.path.join(base_folder, game_name)
    os.makedirs(game_folder, exist_ok=True)
    return game_folder


def _utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _git_revision() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _sanitize_path_component(value: str) -> str:
    sanitized = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            sanitized.append(char)
        else:
            sanitized.append("_")
    return "".join(sanitized).strip("_") or "unknown"


def get_llm_interactions_game_folder(game_folder: str) -> str:
    base_folder = os.path.dirname(game_folder)
    game_name = os.path.basename(game_folder)
    interactions_folder = os.path.join(base_folder, "llm_interactions", game_name)
    os.makedirs(interactions_folder, exist_ok=True)
    return interactions_folder


def build_game_manifest(
    game_master: "GameMaster",
    game_folder: str,
    *,
    include_initial_troop_placement: bool,
) -> Dict[str, object]:
    players = []
    for player in game_master.players:
        llm_client = player.llm_client
        player_entry: Dict[str, object] = {
            "name": player.name,
            "provider": getattr(llm_client, "provider_name", None),
            "model": getattr(llm_client, "model_type", None),
            "turn_time_limit_seconds": player.turn_time_limit_seconds,
            "placement_time_limit_seconds": player.placement_time_limit_seconds,
            "placement_reasoning_effort": player.placement_reasoning_effort,
            "planning_reasoning_effort": player.planning_reasoning_effort,
            "attack_reasoning_effort": player.attack_reasoning_effort,
            "fortify_reasoning_effort": player.fortify_reasoning_effort,
            "card_trade_reasoning_effort": player.card_trade_reasoning_effort,
        }
        for optional_field in (
            "reasoning_effort",
            "verbosity",
            "thinking_effort",
            "thinking_budget",
            "enable_thinking",
            "include_thoughts",
        ):
            if hasattr(llm_client, optional_field):
                player_entry[optional_field] = getattr(llm_client, optional_field)
        players.append(player_entry)

    rules_snapshot = {
        "progressive": game_master.rules.progressive,
        "capitals": game_master.rules.capitals,
        "territory_control_percentage": game_master.rules.territory_control_percentage,
        "required_continents": game_master.rules.required_continents,
        "key_areas": list(game_master.rules.key_areas),
        "max_rounds": game_master.rules.max_rounds,
        "turn_time_limit_seconds": game_master.rules.turn_time_limit_seconds,
        "placement_time_limit_seconds": game_master.rules.placement_time_limit_seconds,
        "placement_reasoning_effort": game_master.rules.placement_reasoning_effort,
        "planning_reasoning_effort": game_master.rules.planning_reasoning_effort,
        "attack_reasoning_effort": game_master.rules.attack_reasoning_effort,
        "fortify_reasoning_effort": game_master.rules.fortify_reasoning_effort,
        "card_trade_reasoning_effort": game_master.rules.card_trade_reasoning_effort,
    }

    return {
        "generated_at_utc": _utc_timestamp(),
        "game_folder": os.path.basename(game_folder),
        "git_revision": _git_revision(),
        "include_initial_troop_placement": include_initial_troop_placement,
        "rules": rules_snapshot,
        "players": players,
    }


def save_game_manifest(
    game_master: "GameMaster",
    game_folder: str,
    *,
    include_initial_troop_placement: bool,
) -> str:
    manifest = build_game_manifest(
        game_master,
        game_folder,
        include_initial_troop_placement=include_initial_troop_placement,
    )
    output_path = os.path.join(game_folder, "game_manifest.json")
    with open(output_path, "w") as file:
        json.dump(manifest, file, indent=2)
    return output_path


def build_llm_interaction_logger(game_folder: str) -> Callable[[Dict[str, object]], None]:
    interactions_folder = get_llm_interactions_game_folder(game_folder)

    def _logger(interaction_entry: Dict[str, object]) -> None:
        player_name = _sanitize_path_component(
            str(interaction_entry.get("player", "unknown_player"))
        )
        phase_name = _sanitize_path_component(
            str(interaction_entry.get("phase", "unknown_phase"))
        )
        game_round = int(interaction_entry.get("game_round") or 0)
        turn_number = interaction_entry.get("turn_number")
        scope = _sanitize_path_component(
            str(interaction_entry.get("scope", "unscoped"))
        )
        interaction_index = int(interaction_entry.get("interaction_index") or 0)

        if turn_number is None:
            turn_folder = scope
        else:
            turn_folder = f"turn_{int(turn_number):04d}"

        output_folder = os.path.join(
            interactions_folder,
            player_name,
            f"round_{game_round:02d}",
            turn_folder,
        )
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(
            output_folder,
            f"{interaction_index:04d}_{phase_name}.json",
        )
        with open(output_path, "w") as file:
            json.dump(interaction_entry, file, indent=2)

    return _logger


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


def save_turn_summary(
    turn_summary: Optional[dict], game_folder: str, turn_number: int
) -> None:
    if turn_summary is None:
        return

    filename = os.path.join(game_folder, f"turn_summary_turn_{turn_number}.json")
    with open(filename, "w") as file:
        json.dump(turn_summary, file, indent=2)

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
