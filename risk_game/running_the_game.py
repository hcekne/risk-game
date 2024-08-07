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

print(f'The last player has index:_{game.game_state.last_player_index}')

# we need to move on to the next player and he needs to do a valid move.

# doesn't really use this anymore
game.players[0].include_reasoning = False
# Make a move
# move = game.players[0].make_initial_troop_placement(game.game_state)
# move onto the next player
game.update_current_player_index()
game.initial_troop_placement()
print(game.game_state.territories_df)

game.game_state.territories_df.to_csv('territories.csv', index=False)

# Access the message content
# message_content = move.choices[0].message.content

# Print the message content
#print(f'the parsed move is: {move}')


#print(f'player {game.players[0].name} has {game.players[0].troops} troops')

# if game.validate_move(game.players[0], move):
#     print("Move is valid")
#     # update the game state
#     game.update_game_state(game.players[0], move)    
#     # reduce the number of troops for the player
#     game.reduce_player_troops(game.players[0], move)
#     # print the game state 
#     # print the number of troops left for the player


# print(f'player {game.players[0].name} has {game.players[0].troops} troops')