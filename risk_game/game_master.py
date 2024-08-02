from typing import List, Tuple
import random
from risk_game.player_agent import PlayerAgent
from risk_game.game_state import GameState
from risk_game.rules import Rules

class GameMaster:
    def __init__(self):
        self.players: List[PlayerAgent] = []
        self.dead_players: List[PlayerAgent] = []
        self.active_players: List[PlayerAgent] = []
        self.game_state = None
        self.rules = Rules()
        self.current_player_index = -1

    def add_player(self, player: PlayerAgent) -> None:
        if len(self.players) >= 6:
            raise ValueError("Cannot add more than 6 players")
        self.players.append(player)

    def init_game_state(self) -> None:
        num_players = len(self.players)
        # only init the game state if there are 2 or more players
        if num_players < 2:
            raise ValueError("Cannot start a game with fewer than 2 players")
        random.shuffle(self.players)
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
            # Adjust current_player_index based on the removed player's position
            if remove_index < self.current_player_index:
                self.current_player_index -= 1
            elif remove_index == self.current_player_index:
                self.current_player_index = self.current_player_index % len(self.active_players)
            # Reset current_player_index if it goes out of bounds
            if self.current_player_index >= len(self.active_players):
                self.current_player_index = 0
        else:
            print(f"Player {player_name} not found in active players")


    def list_players(self) -> None:
        for player in self.players:
            print(f"Name: {player.name}")


    
    def distribute_territories_random(self) -> int:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        self.current_player_index = self.game_state.assign_territories_to_players_random(self.active_players)
        return self.current_player_index

    def get_next_player(self) -> Tuple[int, str]:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        return self.game_state.get_next_player(self.players)

    
    def validate_move(self, player_id, move):
        return self.rules.validate_move(self.game_state, player_id, move)

    def update_game_state(self, player_id, move):
        self.game_state.update(player_id, move)

    def play_game(self):
        while not self.game_state.is_game_over():
            for player in self.players:
                move = player.make_move(self.game_state)
                if self.validate_move(player.id, move):
                    self.update_game_state(player.id, move)

if __name__ == "__main__":
    game = GameMaster()
    game.play_game()
