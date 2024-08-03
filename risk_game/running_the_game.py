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

assert game.game_state.validate_territory_assignment() == True

move = game.players[0].make_initial_troop_placement(game.game_state)


# Access the message content
message_content = move.choices[0].message.content

# Print the message content
print(message_content)