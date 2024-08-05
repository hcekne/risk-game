import json
from typing import Dict,Optional, Tuple
from network_utils import GroqClient

class PlayerAgent:
    def __init__(self, name: str, model_number: int)-> None:
        self.name = name
        self.model_number = model_number
        self.agent_model = GroqClient(model_number)
        self.include_reasoning = True
        self.troops = 0

    def _send_message(self, message_content: str) -> str:
        messages = [
            {
                "role": "user",
                "content": message_content
            }
        ]
        return self.agent_model.get_chat_completion(messages)
    
    def parse_response(
            self, move_response: Dict
    ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        try:
            response_content = move_response.choices[0].message.content
            print(f"Response content: {response_content}") 
            response_json = json.loads(response_content)
            territory = response_json.get('territoryName')
            num_troops = response_json.get('numTroops')
            if self.include_reasoning:
                reasoning = response_json.get('reasoning', None)
                return territory, num_troops, reasoning
            else:
                return territory, num_troops, None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing response: {e}")
            return None, None, None

        
    def make_initial_troop_placement(
            self, game_state: 'GameState') -> str:
        # Implement strategy to make a move
        game_state_json = game_state.territories_df.to_json()

        # Consider also adding a summary of the game so far in your message
        message_content_1 = (
        f'''
        For the following question, please formulate your response as a JSON 
        object, and don't include any additional information. This is most
        important for the grading of your submission.
        We are playing Risk and we are in the troop placement phase.
        The current game state is {game_state_json}. Please suggest a 
        move for {self.name}. You can only place one troop. Think carefully
        about your move and consider also the moves of other players. 
        Format your response as a JSON object with the EXACT following fields 
        and no additional fields or explanations:
        '''
        )
        if self.include_reasoning:
            message_content_2 = (
        '''{"territoryName" (string), "numTroops" (integer), 
        "reasoning" (string)}

        Example response:
        {"territoryName": "Brazil", "numTroops": 1, 
        "reasoning": "Brazil is a key territory in South America and the other
        players are likely to try to take it. I want to make sure I have a 
        presence there."}'''
        )
        else:
            message_content_2 = (
        '''{{"territoryName" (string), "numTroops" (integer)}}

        Example response:
        {{"territoryName": "Brazil", "numTroops": 1}}'''
        )

        message_content_3 = (
        '''Your response should be a valid JSON object with exactly these 
        fields. Do not escape any characters, and do not include backslashes. 
        Please make sure these instuctions are followed to the letter
        and that the response is like the example provided above.'''
        )


        prompt = f"""
        We are playing Risk and we are in the troop placement phase.
        The current game state is {game_state_json}. Please suggest a 
        move for {self.name}. You can only place one troop. Think carefully
        about your move and consider also the moves of other players. 

        Your response should be a comma-separated string with exactly two elements:
        - The first element is the name of the territory.
        - The second element is the number of troops.

        Example response:
        "Brazil,1"
        Do not include any additional text or characters in your response.
        """

        parsed_response = (
            self.parse_response(
                self._send_message(
                message_content_1 + message_content_2+ message_content_3 ))
        )

        return parsed_response
    

