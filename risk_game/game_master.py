from typing import List
from risk_game.player_agent import PlayerAgent
from risk_game.game_state import GameState
from risk_game.rules import Rules

class GameMaster:
    def __init__(self):
        self.players: List[PlayerAgent] = []
        self.dead_players: List[PlayerAgent] = []
        self.game_state = GameState()
        self.rules = Rules()

    def add_player(self, player_name: str) -> None:
        self.players.append(PlayerAgent(player_name))

    def remove_player(self, player_name: str) -> None:
        player_to_remove = None
        for player in self.players:
            if player.name == player_name:
                player_to_remove = player
                break

        if player_to_remove:
            self.players.remove(player_to_remove)
            self.dead_players.append(player_to_remove)

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
