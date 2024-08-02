import pandas as pd
import numpy as np
import random
from typing import Dict, List, Tuple
from risk_game.player_agent import PlayerAgent
from risk_game.utils import TERRITORIES, CONTINENT_BONUSES

class GameState:
    def __init__(self, players: List[PlayerAgent]) -> None:
        self.num_players: int = len(players)
        self.last_player_index: int = -1  # Initialize to -1 indicating no player has acted yet
        self.territories_df: pd.DataFrame = self._init_territories_df(players)
        self.continent_arrays: Dict[str, np.ndarray] = self._init_continent_arrays()
    
    def _init_territories_df(self, players: List[PlayerAgent]) -> pd.DataFrame:
        # Use player names for columns
        print([player.name for player in players])
        columns = ['Territory'] + [f'Player_{player.name}' for player in players]
        territories_df = pd.DataFrame(TERRITORIES, columns=['Territory'])
        for player in players:
            territories_df[f'Player_{player.name}'] = 0
        return territories_df
    
    def _init_continent_arrays(self) -> Dict[str, np.ndarray]:
        # Create a dictionary to hold the arrays for each continent
        continent_arrays = {}
        for continent, (territories, bonus) in CONTINENT_BONUSES.items():
            # Initialize an array with rows equal to the number of territories and columns equal to the number of players
            continent_arrays[continent] = np.zeros((len(territories), self.num_players), dtype=int)
        return continent_arrays
    
    # def assign_territories_to_players_random(self, players: List[PlayerAgent]) -> int:
    #     territories = list(self.territories_df['Territory'])
    #     random.shuffle(territories)

    #     num_players = len(players)
    #     for i, territory in enumerate(territories):
    #         player_index = i % num_players
    #         player_name = players[player_index].name
    #         print(f'Assigning {territory} to {player_name} with index {player_index}')
    #         self.territories_df.loc[self.territories_df['Territory'] == territory, f'Player_{player_name}'] = 1
    #         self.last_player_index = player_index  # Update the last player index to the current player
        
    #     return self.last_player_index
    
    # def assign_territories_to_players_random(self, players: List[PlayerAgent]) -> int:
    #     territories = list(self.territories_df['Territory'])
    #     random.shuffle(territories)

    #     num_players = len(players)
    #     for i, territory in enumerate(territories):
    #         player = players[i % num_players]
    #         player_name = player.name
    #         print(f'Assigning {territory} to {player_name}')
    #         self.territories_df.loc[self.territories_df['Territory'] == territory, f'Player_{player_name}'] = 1
    #         self.last_player_index = i % num_players  # Update the last player index to the current player

    #     return self.last_player_index
    

    def assign_territories_to_players_random(self, players: List[PlayerAgent]) -> int:
        territories = list(self.territories_df['Territory'])
        random.shuffle(territories)

        for i, territory in enumerate(territories):
            player = players[i % self.num_players]
            player_name = player.name
            print(f'Assigning {territory} to {player_name}')
            self.territories_df.loc[self.territories_df['Territory'] == territory, f'Player_{player_name}'] = 1
            self.last_player_index = i % self.num_players  # Update the last player index to the current player
        
        return self.last_player_index

    def get_next_player(self, players: List[PlayerAgent]) -> Tuple[int, str]:
        self.last_player_index = (self.last_player_index + 1) % self.num_players
        next_player = players[self.last_player_index]
        return self.last_player_index, next_player.name

    def validate_territory_assignment(self) -> bool:
        # Sum all the values in the DataFrame
        total_sum = self.territories_df.iloc[:, 1:].sum().sum()  # Sums all player columns
        return total_sum == 42
    
    def update_territory_control(self, territory: str, player_index: int, troops: int) -> None:
        # Update the pandas DataFrame
        self.territories_df.loc[self.territories_df['Territory'] == territory, f'Player {player_index+1}'] = 1
        self.territories_df.loc[self.territories_df['Territory'] == territory, 'Troops'] = troops
        
        # Find which continent the territory belongs to and update control
        for continent, (territories, _) in CONTINENT_BONUSES.items():
            if territory in territories:
                territory_index = territories.index(territory)
                self.continent_arrays[continent][:, player_index] = 0  # Reset previous controls for the player
                self.continent_arrays[continent][territory_index, player_index] = 1  # Set new control
                break
