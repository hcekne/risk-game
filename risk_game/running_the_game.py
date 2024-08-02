# Enable the autoreload extension


# Set autoreload mode


import risk_game.game_master as gm

game = gm.GameMaster()
game.add_player(gm.PlayerAgent(name="Player 1"))
game.add_player(gm.PlayerAgent(name="Player 2"))
#game.add_player(gm.PlayerAgent(name="Player 3"))

print(game.players)  # This should now show PlayerAgent objects
# game.add_player("Player 4")
game.init_game_state()

game.distribute_territories_random()
print(game.game_state.territories_df)

last_player_index = game.game_state.last_player_index

print(f'The last player has index:_{last_player_index}')

print(f'The last player has name:_{game.active_players[last_player_index].name}')  

assert game.game_state.validate_territory_assignment() == True
