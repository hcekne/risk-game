from network_utils import GroqClient

class PlayerAgent:
    def __init__(self, name: str, model_number: int)-> None:
        self.name = name
        self.model_number = model_number
        self.agent_model = GroqClient(model_number)

        
    def make_initial_troop_placement(self, game_state):
        # Implement strategy to make a move
        game_state_json = game_state.territories_df.to_json()

        # Format the message using a multi-line f-string

        # Consider also adding a summary of the game so far in your message
        message_content = (
            f"We are playing Risk and we are in the troop placement phase. "
            f"The current game state is {game_state_json}. "
            f"Please suggest a move for {self.name}. "
            f"You can only place one troop. "
            f"Think carefully about your move and consider also the moves of other players. "
            f"Format your respone as follows: '**Territory Name;Number of Troops**' and don't include any other text in your response."

)

        messages=[
        {
            "role": "user",
            "content": message_content
        }
        ]
        move = self.agent_model.get_chat_completion(messages)
        return move
