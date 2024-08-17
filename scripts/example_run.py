import risk_game.game_master as gm
import risk_game.card_deck as cd
from risk_game.rules import Rules
import pandas as pd
from risk_game.llm_clients import llm_client
import importlib



### PHASE 0: Initialize the game

# Initialize the rules
rules = Rules(progressive=False, capitals=False, mode="world_domination",
                max_rounds=2)


# importlib.reload(gm)

# Initialize the GameMaster with the rules
game = gm.GameMaster(rules)

# game.add_player(name="Player_Player 1", 
#                 llm_client=llm_client.create_llm_client("Groq",1 ))

game.add_player(name="Player_Player 1", 
                llm_client=llm_client.create_llm_client("Bedrock",1 ))

# who_are_you_prompt = game.players[0].send_message("Hello, who are you?")
# print(who_are_you_prompt)

game.add_player(name="Player_Player 2",
                llm_client=llm_client.create_llm_client("Anthropic",1 ))
# who_are_you_prompt = game.players[1].send_message("Hello, who are you?")

#who_are_you_prompt[0].text

#  print(who_are_you_prompt)
# risk_follow_up_quesion = game.players[1].send_message("Are you a specialist in Risk?")
# print(risk_follow_up_quesion)


game.add_player(name="Player_Player 4", 
                llm_client=llm_client.create_llm_client("OpenAI",1 ))

# who_are_you_prompt = game.players[2].send_message("Hello, who are you?")
# print(who_are_you_prompt)



# game.add_player(name="Player_Player 5", 
#                 llm_client=llm_client.create_llm_client("Bedrock",1 ))

# who_are_you_prompt = game.players[3].send_message("Hello, who are you?")
# print(who_are_you_prompt)





print(game.players)  # This should now show PlayerAgent objects
# game.add_player("Player 4")
game.init_game_state()


# a. Log in to the AWS Management Console. 
# b. Navigate to the IAM (Identity and Access Management) service. 
# c. Select 'Users' from the left sidebar, then choose your user name. 
# d. Go to the 'Security Credentials' tab. 
# e. Under 'Access keys (access key ID and secret access key)', 
# create a new access key if you don't have one already.

# game.distribute_territories_random()

# if game.rules.capitals:
#     game.choose_capitals()
# print(game.game_state.territories_df)

# print(f'The last player has index:_{game.game_state.last_player_index}')

card_deck = cd.Deck()


# doesn't really use this anymore
# game.players[0].include_reasoning = False
# Make a move
# move = game.players[0].make_initial_troop_placement(game.game_state)
# move onto the next player
# game.update_current_player_index()
# game.initial_troop_placement()
# print(game.game_state.territories_df)

# game.game_state.territories_df.to_csv('territories.csv', index=False)

game.game_state.territories_df = pd.read_csv('territories.csv')
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

game.play_game()

