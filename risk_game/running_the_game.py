import risk_game.game_master as gm

game = gm.GameMaster()
game.add_player(name="Player 1", model_number=1)
game.add_player(name="Player 2", model_number=2)
game.add_player(name="Player 4", model_number=4)

print(game.players)  # This should now show PlayerAgent objects
# game.add_player("Player 4")
game.init_game_state()

game.distribute_territories_random()
print(game.game_state.territories_df)

last_player_index = game.game_state.last_player_index

print(f'The last player has index:_{last_player_index}')

print(f'The last player has name:_{game.active_players[last_player_index].name}')  

try:
    result = game.game_state.validate_territory_assignment()
    print(f"Validation result: {result}")
    assert result == True
except Exception as e:
    print(f"An error occurred: {e}")

# don't include reasoning
game.players[0].include_reasoning = False
# Make a move
move = game.players[0].make_initial_troop_placement(game.game_state)


# Access the message content
# message_content = move.choices[0].message.content

# Print the message content
print(f'the parsed move is: {move}')


print(f'player {game.players[0].name} has {game.players[0].troops} troops')

if game.validate_move(game.players[0], move):
    print("Move is valid")
    # update the game state
    game.update_game_state(game.players[0], move)    
    # reduce the number of troops for the player
    game.reduce_player_troops(game.players[0], move)
    # print the game state 
    # print the number of troops left for the player


print(f'player {game.players[0].name} has {game.players[0].troops} troops')