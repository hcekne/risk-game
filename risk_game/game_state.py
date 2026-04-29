from collections import deque
import pandas as pd
import math
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from risk_game.game_constants import TERRITORIES, CONTINENT_BONUSES, \
TERRITORY_CONNECTIONS

class GameState:
    def __init__(self,
                 players: List['PlayerAgent'], rules: 'Rules') -> None: 
        self.num_players: int = len(players)
        # Initialize to -1 indicating no player has acted yet
        self.last_player_index: int = -1
        self.capitals: Dict[str, str] = {} # store capitals for each player
        self.territories_df: pd.DataFrame = self._init_territories_df(players)
        # Graph of territory connections
        self.territories_graph: Dict[str, List[str]] = TERRITORY_CONNECTIONS 
        self.rules = rules
        self.territories_required_to_win = math.ceil(
            self.rules.territory_control_percentage * len(TERRITORIES))
    
    def _init_territories_df(self, players: List['PlayerAgent']) -> pd.DataFrame:
        # Use player names for columns
        print([player.name for player in players])
        columns = ['Territory'] + [f'{player.name}' for player in players]
        territories_df = pd.DataFrame(TERRITORIES, columns=['Territory'])
        for player in players:
            territories_df[f'{player.name}'] = 0
        return territories_df

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

    def get_player_territories_with_troops(
        self, player_name: str
    ) -> List[Tuple[str, int]]:
        territories = self.territories_df[self.territories_df[f"{player_name}"] > 0]
        return [
            (row["Territory"], int(row[player_name]))
            for _, row in territories.iterrows()
        ]
    
    def has_remaining_territories(self, player_name: str) -> bool:
        return len(self.get_player_territories(player_name)) > 0     

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

            # print(f'----#-#-#-#-##-Neighbors of {territory}: {neighbors}')
            
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
        )-> Tuple[str, str]:

        territory = move[0].get('territory_name')
        num_troops = move[0].get('num_troops')

        if territory == 'Blank' or num_troops == 0:
            return ('no_attack', "_")  # Blank move is valid
        
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
            return ('win', defender_name)
        else:
            # update the troops for the defender
            self.update_troops(defender_name, territory, remaining_troops,
                               set_troops=True)
            return ('lose', defender_name)

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

    def get_player_aliases(self) -> Dict[str, str]:
        return {
            player_name: f"P{index + 1}"
            for index, player_name in enumerate(self.territories_df.columns[1:])
        }

    def get_player_status(self, player_name: str) -> Dict[str, object]:
        territories = self.get_player_territories(player_name)
        controlled_continents = [
            continent
            for continent, (continent_territories, _) in CONTINENT_BONUSES.items()
            if all(territory in territories for territory in continent_territories)
        ]
        return {
            "territories": len(territories),
            "troops": self.get_sum_of_player_troops(player_name),
            "capital": self.capitals.get(player_name),
            "continents": controlled_continents,
        }

    def get_continent_progress(
        self, player_name: str
    ) -> List[Tuple[str, int, int, int]]:
        progress = []
        player_territories = set(self.get_player_territories(player_name))
        for continent, (territories, bonus) in CONTINENT_BONUSES.items():
            controlled = sum(1 for territory in territories if territory in player_territories)
            progress.append((continent, controlled, len(territories), bonus))

        progress.sort(key=lambda item: (item[1] / item[2], item[1], item[3]), reverse=True)
        return progress

    def get_border_territories(
        self, player_name: str
    ) -> List[Tuple[str, int, List[Tuple[str, str, int]]]]:
        border_territories = []
        for territory in sorted(self.get_player_territories(player_name)):
            enemy_neighbors = []
            for neighbor in sorted(self.territories_graph.get(territory, [])):
                control = self.get_territory_control(neighbor)
                if control is None:
                    continue
                owner, troops = control
                if owner != player_name:
                    enemy_neighbors.append((neighbor, owner, troops))

            if enemy_neighbors:
                border_territories.append(
                    (
                        territory,
                        self.check_number_of_troops(player_name, territory),
                        enemy_neighbors,
                    )
                )

        border_territories.sort(
            key=lambda item: (len(item[2]), item[1], item[0]),
            reverse=True,
        )
        return border_territories

    def get_interior_reserves(self, player_name: str) -> List[Tuple[str, int]]:
        interior_reserves = []
        for territory, movable_troops in self.get_strong_territories_with_troops(player_name):
            if all(
                self.check_terr_control(player_name, neighbor)
                for neighbor in self.territories_graph.get(territory, [])
            ):
                interior_reserves.append((territory, movable_troops))

        interior_reserves.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return interior_reserves

    def get_fortify_options(
        self, player_name: str
    ) -> Dict[str, List[Tuple[str, int, int]]]:
        border_targets = [territory for territory, _, _ in self.get_border_territories(player_name)]
        fortify_options = {}

        for from_territory, movable_troops in self.get_strong_territories_with_troops(player_name):
            legal_targets = []
            for target_territory in border_targets:
                if target_territory == from_territory:
                    continue
                if self.are_territories_connected(player_name, from_territory, target_territory):
                    enemy_count = sum(
                        1
                        for neighbor in self.territories_graph[target_territory]
                        if not self.check_terr_control(player_name, neighbor)
                    )
                    legal_targets.append(
                        (
                            target_territory,
                            self.check_number_of_troops(player_name, target_territory),
                            enemy_count,
                        )
                    )

            legal_targets.sort(key=lambda item: (item[2], item[1], item[0]), reverse=True)
            if legal_targets:
                fortify_options[from_territory] = legal_targets

        return fortify_options

    def format_world_map_compact(self) -> str:
        aliases = self.get_player_aliases()
        lines = ["World map by continent (territory=player_alias:troops):"]
        for continent, (territories, bonus) in CONTINENT_BONUSES.items():
            territory_parts = []
            for territory in territories:
                control = self.get_territory_control(territory)
                if control is None:
                    territory_parts.append(f"{territory}=_:0")
                    continue
                owner, troops = control
                territory_parts.append(f"{territory}={aliases.get(owner, owner)}:{troops}")
            lines.append(f"- {continent}(+{bonus}): " + " | ".join(territory_parts))

        return "\n".join(lines)

    def format_player_territory_list(
        self, player_name: str, sort_desc: bool = True, limit: Optional[int] = None
    ) -> str:
        territories_with_troops = self.get_player_territories_with_troops(player_name)
        territories_with_troops.sort(
            key=lambda item: (item[1], item[0]),
            reverse=sort_desc,
        )
        if limit is not None:
            territories_with_troops = territories_with_troops[:limit]

        if not territories_with_troops:
            return "none"

        return ", ".join(
            f"{territory}({troops})"
            for territory, troops in territories_with_troops
        )

    def get_territory_continent(self, territory: str) -> Optional[str]:
        for continent, (territories, _) in CONTINENT_BONUSES.items():
            if territory in territories:
                return continent
        return None

    def format_placement_targets_with_context(
        self,
        player_name: str,
        limit: Optional[int] = None,
    ) -> str:
        aliases = self.get_player_aliases()
        border_lookup = {
            territory: (troops, enemy_neighbors)
            for territory, troops, enemy_neighbors in self.get_border_territories(player_name)
        }
        target_lines: list[tuple[tuple[int, int, int, str], str]] = []

        for territory, troops in self.get_player_territories_with_troops(player_name):
            continent = self.get_territory_continent(territory) or "Unknown"
            if territory in border_lookup:
                _, enemy_neighbors = border_lookup[territory]
                enemy_preview = ", ".join(
                    f"{neighbor} {aliases[owner]}({enemy_troops})"
                    for neighbor, owner, enemy_troops in enemy_neighbors[:3]
                )
                line = (
                    f"- {territory}({troops}) [{continent}] "
                    f"enemy_neighbors={len(enemy_neighbors)}"
                )
                if enemy_preview:
                    line += f" -> {enemy_preview}"
                sort_key = (0, -len(enemy_neighbors), -troops, territory)
            else:
                line = f"- {territory}({troops}) [{continent}] interior"
                sort_key = (1, 0, -troops, territory)
            target_lines.append((sort_key, line))

        target_lines.sort(key=lambda item: item[0])
        if limit is not None:
            target_lines = target_lines[:limit]

        if not target_lines:
            return "- none"

        return "\n".join(line for _, line in target_lines)

    def format_placement_state_for_player(self, player_name: str) -> str:
        aliases = self.get_player_aliases()
        player_status = self.get_player_status(player_name)
        opponent_statuses = [
            (other_player, self.get_player_status(other_player))
            for other_player in self.territories_df.columns[1:]
            if other_player != player_name
        ]
        leader_name, leader_status = max(
            opponent_statuses + [(player_name, player_status)],
            key=lambda item: (item[1]["territories"], item[1]["troops"]),
        )
        remaining_to_win = max(
            self.territories_required_to_win - player_status["territories"],
            0,
        )

        lines = [
            "Placement snapshot:",
            (
                f"You hold {player_status['territories']} territories and "
                f"{player_status['troops']} troops on board."
            ),
            (
                f"Win target: {self.territories_required_to_win}/{len(TERRITORIES)} "
                f"territories; need {remaining_to_win} more."
            ),
            (
                f"Current leader: {aliases[leader_name]} ({leader_name}) "
                f"terr={leader_status['territories']} troops={leader_status['troops']}"
            ),
            "",
            "Continent progress:",
        ]

        for continent, controlled, total, bonus in self.get_continent_progress(player_name):
            lines.append(f"- {continent}(+{bonus}): {controlled}/{total}")

        lines.extend(["", "Top pressure points:"])
        border_territories = self.get_border_territories(player_name)
        if border_territories:
            for territory, troops, enemy_neighbors in border_territories[:6]:
                continent = self.get_territory_continent(territory) or "Unknown"
                enemy_preview = ", ".join(
                    f"{neighbor} {aliases[owner]}({enemy_troops})"
                    for neighbor, owner, enemy_troops in enemy_neighbors[:3]
                )
                line = (
                    f"- {territory}({troops}) [{continent}] "
                    f"enemy_neighbors={len(enemy_neighbors)}"
                )
                if enemy_preview:
                    line += f" -> {enemy_preview}"
                lines.append(line)
        else:
            lines.append("- none")

        return "\n".join(lines)

    def format_game_state_for_player(
        self, player_name: str, include_world_map: bool = True
    ) -> str:
        aliases = self.get_player_aliases()
        player_status = self.get_player_status(player_name)
        ordered_players = [player_name] + [
            other_player
            for other_player in self.territories_df.columns[1:]
            if other_player != player_name
        ]

        lines = [
            "Game snapshot:",
            "Player key: " + ", ".join(
                f"{alias}={name}" for name, alias in aliases.items()
            ),
            (
                f"You are {aliases[player_name]} ({player_name}). "
                f"Win target: {self.territories_required_to_win}/{len(TERRITORIES)} territories. "
                f"You hold {player_status['territories']} and need "
                f"{max(self.territories_required_to_win - player_status['territories'], 0)} more."
            ),
            "",
            "Standings:",
        ]

        for current_player in ordered_players:
            current_status = self.get_player_status(current_player)
            status_line = (
                f"- {aliases[current_player]} ({current_player}): "
                f"terr={current_status['territories']} "
                f"troops={current_status['troops']}"
            )
            if current_status["capital"]:
                status_line += f" capital={current_status['capital']}"
            if current_status["continents"]:
                status_line += (
                    " continents=" + ",".join(current_status["continents"])
                )
            lines.append(status_line)

        lines.extend(["", "Your continent progress:"])
        for continent, controlled, total, bonus in self.get_continent_progress(player_name):
            lines.append(f"- {continent}(+{bonus}): {controlled}/{total}")

        border_territories = self.get_border_territories(player_name)
        lines.extend(["", "Your borders:"])
        if border_territories:
            for territory, troops, enemy_neighbors in border_territories[:8]:
                enemy_text = ", ".join(
                    f"{neighbor} {aliases[owner]}({enemy_troops})"
                    for neighbor, owner, enemy_troops in enemy_neighbors[:4]
                )
                lines.append(f"- {territory}({troops}) -> {enemy_text}")
        else:
            lines.append("- none")

        interior_reserves = self.get_interior_reserves(player_name)
        lines.extend(["", "Your interior reserves:"])
        if interior_reserves:
            reserve_text = ", ".join(
                f"{territory} can_move={movable_troops}"
                for territory, movable_troops in interior_reserves[:6]
            )
            lines.append(f"- {reserve_text}")
        else:
            lines.append("- none")

        if include_world_map:
            lines.extend(["", self.format_world_map_compact()])

        return "\n".join(lines)
    
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
        self, adjacent_enemy_territories: Dict[str, List], player_name: Optional[str] = None
    ) -> str:
        """
        Format the adjacent enemy territories dictionary into a human-readable string.
        
        Parameters:
        - adjacent_enemy_territories: A dictionary where the keys are the territories and
        the values are lists containing the number of attacking troops and the list of
        adjacent enemy territories.
        
        Returns:
        - A formatted string representing the adjacent enemy territories in a human-readable format.
        """
        aliases = self.get_player_aliases()
        formatted_output = ["Attack options:"]

        for territory, (attacking_troops, enemy_territories) in adjacent_enemy_territories.items():
            if enemy_territories:
                enemy_parts = []
                for enemy_territory in enemy_territories:
                    control = self.get_territory_control(enemy_territory)
                    if control is None:
                        enemy_parts.append(f"{enemy_territory} _:0")
                        continue
                    owner, troops = control
                    owner_text = aliases.get(owner, owner) if player_name else owner
                    enemy_parts.append(f"{enemy_territory} {owner_text}({troops})")
                formatted_output.append(
                    f"- {territory} max={attacking_troops} -> {', '.join(enemy_parts)}"
                )
            else:
                formatted_output.append(
                    f"- {territory} max={attacking_troops} -> no enemy neighbors"
                )

        if len(formatted_output) == 1:
            formatted_output.append("- no legal attacks")

        return "\n".join(formatted_output)

    def format_fortify_options(self, player_name: str) -> str:
        fortify_options = self.get_fortify_options(player_name)
        lines = ["Fortify options (legal connected border targets only):"]

        for from_territory, legal_targets in fortify_options.items():
            movable_troops = self.check_number_of_troops(player_name, from_territory) - 1
            target_text = ", ".join(
                f"{target}({target_troops}, enemy_neighbors={enemy_count})"
                for target, target_troops, enemy_count in legal_targets[:5]
            )
            lines.append(f"- From {from_territory} max={movable_troops} -> {target_text}")

        if len(lines) == 1:
            lines.append("- no useful fortify moves")

        return "\n".join(lines)

    def get_sum_of_player_troops(self, player_name: str) -> int:
        return self.territories_df[f'{player_name}'].sum()

    
     
