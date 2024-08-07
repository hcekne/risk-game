from typing import List, Optional, Tuple
import random
from risk_game.player_agent import PlayerAgent
from risk_game.game_state import GameState
from risk_game.rules import Rules

class GameMaster:
    def __init__(self)-> None:
        self.players: List[PlayerAgent] = []
        self.dead_players: List[PlayerAgent] = []
        self.active_players: List[PlayerAgent] = []
        self.game_state = None
        self.rules = Rules()
        self.current_player_index = -1

    def add_player(self, name:str, model_number:int) -> None:
        if len(self.players) >= 6:
            raise ValueError("Cannot add more than 6 players")
        self.players.append(PlayerAgent(name, model_number))

    def calculate_initial_troops(self, num_players: int) -> int:
        initial_troops_map = {2: 40,3: 35, 4: 30,5: 25,6: 20}
        return initial_troops_map[num_players]

    def init_game_state(self) -> None:
        num_players = len(self.players)
        # only init the game state if there are 2 or more players
        if num_players < 2:
            raise ValueError("Cannot start a game with fewer than 2 players")
        random.shuffle(self.players)
        intial_troops = self.calculate_initial_troops(num_players)
        for player in self.players:
            player.troops = intial_troops
        self.active_players = self.players.copy()
        self.game_state = GameState(self.active_players)

    def remove_player(self, player_name: str) -> None:
        player_to_remove = None
        remove_index = -1
        for i, player in enumerate(self.active_players):
            if player.name == player_name:
                player_to_remove = player
                remove_index = i
                break
        print(f"Index of Player to remove: {remove_index}")

        if player_to_remove:
            self.active_players.remove(player_to_remove)
            self.dead_players.append(player_to_remove)
            self.game_state.num_players = len(self.active_players)
            # Adjust current_player_index based on the removed player's position
            if remove_index < self.current_player_index:
                self.current_player_index -= 1
            elif remove_index == self.current_player_index:
                self.current_player_index = (
                    self.current_player_index % len(self.active_players)
                )
            # Reset current_player_index if it goes out of bounds
            if self.current_player_index >= len(self.active_players):
                self.current_player_index = 0
        else:
            print(f"Player {player_name} not found in active players")


    def list_players(self) -> None:
        for player in self.players:
            print(f"Name: {player.name}")

    def validate_move(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
        ) -> bool:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        print(f"Territory: {territory}, Num troops: {num_troops}")
        if territory is None or num_troops is None:
            print(f"Error: Territory or num_troops is None")
            return False
        if not self.game_state.check_terr_control(player.name, territory):
            print(f"Error: {player.name} does not control territory {territory}")
            return False
        if num_troops > player.troops:
            print(f'''
                  Error: Not enough troops to place. {player.name} has only 
                  {player.troops} troop(s) left.'''
            )
            return False
        return True


    def update_current_player_index(self):
        self.current_player_index = (
            (self.current_player_index + 1) % len(self.active_players)
        )
    
    def distribute_territories_random(self) -> int:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        self.current_player_index = (
            self.game_state.assign_territories_to_players_random(self.active_players))
        return self.current_player_index
    


    # not used yet
    def get_next_player(self) -> Tuple[int, str]:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        return self.game_state.get_next_player(self.players)


    def update_game_state(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
    ) -> None:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        self.game_state.update_troops(player, territory, num_troops)


    def reduce_player_troops(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
    ) -> None:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        player.troops -= num_troops

    def ensure_valid_move(self, player: 'PlayerAgent'):
        valid_move = False
        while not valid_move:
            move = player.make_initial_troop_placement(self.game_state)
            print(f"Proposed move: {move}")
            if self.validate_move(player, move):
                print("Move is valid")
                self.update_game_state(player, move)
                self.reduce_player_troops(player, move)
                valid_move = True
            else:
                print("Move is invalid, asking for a new move")

    def initial_troop_placement(self):
        #self.current_player_index = 0
        while any(player.troops > 0 for player in self.active_players):
            current_player = self.active_players[self.current_player_index]
            print(f"*****-------------NOW PLACING TROOPS FOR: -------------*****")
            print(f"Current player name: {current_player.name}")
            if current_player.troops > 0:
                self.ensure_valid_move(current_player)
            # Move to the next player
            self.current_player_index = (
                (self.current_player_index + 1) % len(self.active_players)
            )
        print("Initial troop placement complete")

    



    def play_game(self):
        while not self.game_state.is_game_over():
            for player in self.players:
                move = player.make_move(self.game_state)
                if self.validate_move(player.id, move):
                    self.update_game_state(player.id, move)

if __name__ == "__main__":
    game = GameMaster()
    game.play_game()
