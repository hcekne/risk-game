from collections import deque
import pandas as pd
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
# from risk_game.player_agent import PlayerAgent
from risk_game.game_utils import TERRITORIES, CONTINENT_BONUSES, \
TERRITORY_CONNECTIONS

class GameState:
    def __init__(self,
                 players: List['PlayerAgent']) -> None: 
        self.num_players: int = len(players)
        # Initialize to -1 indicating no player has acted yet
        self.last_player_index: int = -1
        self.capitals: Dict[str, str] = {} # store capitals for each player
        self.territories_df: pd.DataFrame = self._init_territories_df(players)
        # Graph of territory connections
        self.territories_graph: Dict[str, List[str]] = TERRITORY_CONNECTIONS  
        self.continent_arrays: Dict[str, np.ndarray] = self._init_continent_arrays()
    
    def _init_territories_df(self, players: List['PlayerAgent']) -> pd.DataFrame:
        # Use player names for columns
        print([player.name for player in players])
        columns = ['Territory'] + [f'{player.name}' for player in players]
        territories_df = pd.DataFrame(TERRITORIES, columns=['Territory'])
        for player in players:
            territories_df[f'{player.name}'] = 0
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
                f'{player_name}'
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
    
    def check_terr_control(self, player_name: str, territory: str) -> bool:
        controlled = self.territories_df.loc[
            self.territories_df['Territory'] == territory, 
            f'{player_name}'
        ]
        if controlled.empty:
            return False
        return controlled.values[0] > 0
    
    def are_territories_connected(
            self, player_name: str, from_territory: str, to_territory: str
        ) -> bool:
        """Check if two territories are connected by a chain of territories 
        under the player's control."""
        # breath first search setup
        queue = deque([from_territory])
        visited = set()
        while queue:
            current_territory = queue.popleft()
            
            if current_territory == to_territory:
                return True
            
            visited.add(current_territory)
            
            # Explore neighbors
            for neighbor in self.territories_graph[current_territory]:
                if neighbor not in visited and (
                    self.check_terr_control(player_name, neighbor)):
                    queue.append(neighbor)
        
        return False

    def check_number_of_troops(self, player_name: str, territory: str) -> int:
        controlled = self.territories_df.loc[
            self.territories_df['Territory'] == territory, 
            f'{player_name}'
        ]
        if controlled.empty:
            return 0
        return controlled.values[0]
    
    def update_troops(
        self, player_name: str, 
        territory: Optional[str], num_troops: Optional[int], 
        set_troops: bool = False
    ) -> None:
        if territory and num_troops is not None:
            if set_troops:
                self.territories_df.loc[
                    self.territories_df['Territory'] == territory, 
                    f'{player_name}'
                ] = num_troops
            else:
                self.territories_df.loc[
                    self.territories_df['Territory'] == territory, 
                    f'{player_name}'
                ] += num_troops
        else:
            print(
                f'''Invalid move data: territory={territory}, 
                num_troops={num_troops}'''
            )

    def get_strong_territories(self, player_name: str) -> List[str]:
        # Construct the column name for the player
        player_column = f'{player_name}'
        
        # Filter the DataFrame to get territories with more than 1 troop
        strong_territories = self.territories_df[
            (self.territories_df[player_column] > 1)
        ]['Territory'].tolist()
        
        return strong_territories
    
    def get_strong_territories_with_troops(self, player_name: str
        ) -> List[Tuple[str, int]]:
        # Construct the column name for the player
        player_column = f'{player_name}'
        
        # Filter the DataFrame to get territories with more than 1 troop
        strong_territories_df = self.territories_df[
            self.territories_df[player_column] > 1
        ]
        
        # Create a list of tuples containing the territory name and troops - 1
        strong_territories_with_troops = [
            (row['Territory'], row[player_column] - 1)
            for _, row in strong_territories_df.iterrows()
        ]
        
        return strong_territories_with_troops

    def get_player_territories(self, player_name: str) -> List[str]:
        return list(self.territories_df[
            self.territories_df[f'{player_name}'] > 0]['Territory'])
        

    def get_adjacent_enemy_territories(
        self, player_name: str, territories_with_troops: List[Tuple[str, int]]
    ) -> Dict[str, List]:
        """
        For each territory in the input list, return a list containing the number of
        possible attacking troops and a list of adjacent territories that are not under
        the player's control.
        
        Parameters:
        - player_name: The name of the player.
        - territories_with_troops: A list of tuples where each tuple contains a territory
        name and the number of troops available for attacking from that territory.
        
        Returns:
        - A dictionary where the keys are the territories from the input list, and the values
        are lists containing the number of possible attacking troops and a list of adjacent
        territories not under the player's control.
        """
        adjacent_enemy_territories = {}

        for territory, attacking_troops in territories_with_troops:
            # Get the neighbors (adjacent territories) of the current territory
            neighbors = self.territories_graph.get(territory, [])

            print(f'----#-#-#-#-##-Neighbors of {territory}: {neighbors}')
            
            # List to store adjacent territories not under the player's control
            enemy_territories = []
            
            for neighbor in neighbors:
                if not self.check_terr_control(player_name, neighbor):
                    enemy_territories.append(neighbor)
            
            # Add the result to the dictionary
            adjacent_enemy_territories[territory] = [attacking_troops, enemy_territories]
        
        return adjacent_enemy_territories
    
    
    def is_capital(self, territory: str) -> bool:
        # Check if the territory is a capital
        return territory in self.capitals.values()
    
    def set_capital(self, player_name: str, territory: str):
        # Set the capital for a player
        self.capitals[player_name] = territory

    def check_if_adjacent(self, territory1: str, territory2: str) -> bool:
        return territory2 in self.territories_graph[territory1]
    
    def get_territory_control(self, territory: str) -> Optional[Tuple[str, int]]:
        # Find the row corresponding to the territory
        territory_row = (
            self.territories_df[self.territories_df['Territory'] == territory])
        
        # Iterate over each player column
        for column in territory_row.columns[1:]:  # Skips the 'Territory' column
            troops = territory_row[column].values[0]
            if troops > 0:
                player_name = column
                return player_name, troops
        
        return None  # If no player controls the territory
    
    def update_game_state_for_attack_move(
        self, player: 'PlayerAgent', 
        move: List[Dict[str, int]], 
        from_territory: [str]
        )-> str:

        territory = move[0].get('territory_name')
        num_troops = move[0].get('num_troops')

        if territory == 'Blank' or num_troops == 0:
            return 'no_attack'  # Blank move is valid
        
        original_troops = self.check_number_of_troops(player.name, 
                                                          from_territory)
        new_troops = original_troops - num_troops

        defender_name, defender_troops = self.get_territory_control(territory)

        winner, remaining_troops = self.simulate_attack(num_troops, 
                                                        defender_troops)
        
        # attacker always loses the number of troops used in the attack
        # from the attacking territory
        self.update_troops(player.name, from_territory, -num_troops)
        
        if winner == 'attacker':
            # upodate the troops for the attacker and defender
            self.update_troops(player.name, territory, remaining_troops,
                               set_troops=True)
            self.update_troops(defender_name, territory, 0,
                               set_troops=True)
            return 'win'
        else:
            # update the troops for the defender
            self.update_troops(defender_name, territory, remaining_troops,
                               set_troops=True)
            return 'lose'

    def simulate_attack(self, attacking_troops: int, defending_troops: int
        ) -> Tuple[str, int]:
        """
        Simulate the outcome of an attack in Risk.

        Parameters:
        - attacking_troops (int): Number of troops attacking.
        - defending_troops (int): Number of troops defending.

        Returns:
        - Tuple[str, int]: The winner ('attacker' or 'defender') and the number of troops left.
        """

        while attacking_troops > 0 and defending_troops > 0:
            # Determine the number of dice each side rolls
            attacker_dice = min(attacking_troops, 3)
            defender_dice = min(defending_troops, 2)

            # Roll the dice
            attacker_rolls = sorted([random.randint(1, 6) for _ in range(attacker_dice)], reverse=True)
            defender_rolls = sorted([random.randint(1, 6) for _ in range(defender_dice)], reverse=True)

            # Compare the highest rolls
            for attack_roll, defend_roll in zip(attacker_rolls, defender_rolls):
                if attack_roll > defend_roll:
                    defending_troops -= 1
                else:
                    attacking_troops -= 1

        # Determine the winner
        if defending_troops == 0:
            return 'attacker', attacking_troops
        else:
            return 'defender', defending_troops
        
    def format_game_state(self) -> str:
        # Initialize formatted game state string
        formatted_game_state = "Current Game State:\n\n"
        
        # Iterate through continents using CONTINENT_BONUSES
        for continent, (territories, bonus) in CONTINENT_BONUSES.items():
            formatted_game_state += (f"Continent: {continent} (Bonus: " +
                                    f"{bonus} troops)\n")
            
            # Iterate through territories in each continent
            for territory in territories:
                row = self.territories_df[(
                    self.territories_df['Territory'] == territory)].iloc[0]
                
                # Identify the player who controls the territory and the number of troops
                for col in self.territories_df.columns[1:]:  # Skip the 'Territory' column
                    troops = row[col]
                    if troops > 0:
                        player_name = col
                        formatted_game_state += (
                            f"  - {territory}: Controlled by {player_name} " +
                            f"with {troops} troops\n")
                        break
            
            formatted_game_state += "\n"  # Add a blank line between continents
        
        return formatted_game_state
    
    def format_strong_territories(self, 
        strong_territories_with_troops: List[Tuple[str, int]], player_name: str
    ) -> str:
        formatted_strong_territories = f"Strong Territories for {player_name}:\n\n"

        # Iterate through the list of strong territories and format the output
        for territory, troops in strong_territories_with_troops:
            formatted_strong_territories += (
                f"  - {territory}: {troops} troops available for attack\n"
            )

        return formatted_strong_territories
    
    def format_adjacent_enemy_territories(
        self, adjacent_enemy_territories: Dict[str, List]) -> str:
        """
        Format the adjacent enemy territories dictionary into a human-readable string.
        
        Parameters:
        - adjacent_enemy_territories: A dictionary where the keys are the territories and
        the values are lists containing the number of attacking troops and the list of
        adjacent enemy territories.
        
        Returns:
        - A formatted string representing the adjacent enemy territories in a human-readable format.
        """
        formatted_output = ("The following is list of territories you control " +
            "and the adjacent enemy territories available to attack:\n\n")

        for territory, (attacking_troops, enemy_territories) in adjacent_enemy_territories.items():
            formatted_output += f"{territory}:\n"
            formatted_output += f"  - Maximum Available Attacking Troops: {attacking_troops}\n"
            if enemy_territories:
                formatted_output += f"  - Adjacent Enemy Territories: {', '.join(enemy_territories)}\n"
            else:
                formatted_output += "  - No adjacent enemy territories.\n"
            formatted_output += "\n"  # Add a blank line for readability
        
        return formatted_output

    

    
     