from risk-game.player_agent import PlayerAgent
from risk-game.game_state import GameState
from risk-game.rules import Rules

class GameMaster:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = [PlayerAgent(i) for i in range(num_players)]
        self.game_state = GameState()
        self.rules = Rules()

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
    num_players = 3
    game = GameMaster(num_players)
    game.play_game()
