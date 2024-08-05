import pandas as pd
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
# from risk_game.player_agent import PlayerAgent
from risk_game.game_utils import TERRITORIES, CONTINENT_BONUSES

class GameState:
    def __init__(self, players: List['PlayerAgent']) -> None: 
        self.num_players: int = len(players)
        # Initialize to -1 indicating no player has acted yet
        self.last_player_index: int = -1  
        self.territories_df: pd.DataFrame = self._init_territories_df(players)
        self.continent_arrays: Dict[str, np.ndarray] = self._init_continent_arrays()
    
    def _init_territories_df(self, players: List['PlayerAgent']) -> pd.DataFrame:
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
            # Initialize an array with rows equal to the number of territories 
            # and columns equal to the number of players
            continent_arrays[continent] = np.zeros(
                (len(territories), self.num_players), dtype=int)
        return continent_arrays
    

    def assign_territories_to_players_random(
            self, players: List['PlayerAgent']
    ) -> int:
        territories = list(self.territories_df['Territory'])
        random.shuffle(territories)

        for i, territory in enumerate(territories):
            player = players[i % self.num_players]
            player_name = player.name
            print(f'Assigning {territory} to {player_name}')
            self.territories_df.loc[
                self.territories_df['Territory'] == territory, 
                f'Player_{player_name}'
            ] = 1
            player.troops -= 1 # Remove one troop from the player
            # Update the last player index to the current player
            self.last_player_index = i % self.num_players  
        
        return self.last_player_index

    
    def get_next_player(self, players: List['PlayerAgent']) -> Tuple[int, str]:
        self.last_player_index = (self.last_player_index + 1) % self.num_players
        next_player = players[self.last_player_index]
        return self.last_player_index, next_player.name

    def validate_territory_assignment(self) -> bool:
        # Sum all the values in the DataFrame
        # Sums all player columns
        total_sum = self.territories_df.iloc[:, 1:].sum().sum()  
        return total_sum == 42
    
    def check_terr_control(self, player_name : str, territory: str) -> bool:
        return self.territories_df.loc[
            self.territories_df['Territory'] == territory, 
            f'Player_{player_name}'
        ].values[0] > 0
    

    def update_troops(
        self, player: 'PlayerAgent', 
        territory: Optional[str], num_troops: Optional[int]
    ) -> None:
        if territory and num_troops is not None:
            self.territories_df.loc[
                self.territories_df['Territory'] == territory, 
                f'Player_{player.name}'
            ] += num_troops
        else:
            print(
                f'''Invalid move data: territory={territory}, 
                num_troops={num_troops}'''
            )
