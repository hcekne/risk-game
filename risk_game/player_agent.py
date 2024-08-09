import json
import re
from typing import Dict,Optional,List,Tuple
from network_utils import GroqClient

class PlayerAgent:
    def __init__(self, name: str, model_number: int)-> None:
        self.name: str = name
        self.model_number: int = model_number
        self.agent_model = GroqClient(model_number)
        self.include_reasoning: bool = True
        self.troops: int = 0
        self.cards: List[Dict[str,str]]= []

    def _send_message(self, message_content: str) -> str:
        messages = [
            {
                "role": "user",
                "content": message_content
            }
        ]
        return self.agent_model.get_chat_completion(messages)
    
    # def parse_response(
    #         self, move_response: Dict
    # ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    #     try:
    #         response_content = move_response.choices[0].message.content
    #         print(f"Response content: {response_content}") 
    #         response_json = json.loads(response_content)
    #         territory = response_json.get('territoryName')
    #         num_troops = response_json.get('numTroops')
    #         if self.include_reasoning:
    #             reasoning = response_json.get('reasoning', None)
    #             return territory, num_troops, reasoning
    #         else:
    #             return territory, num_troops, None
    #     except (json.JSONDecodeError, KeyError) as e:
    #         print(f"Error parsing response: {e}")
    #         return None, None, None
        
    # # Parsing the response
    # def parse_csv_response(
    #         self, move_response: Dict
    #     ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    #     response = move_response.choices[0].message.content
    #     print(f"Response content: {response}")
        
    #     if self.include_reasoning:
    #         try:
    #             territory, num_troops, reasoning = response.strip('"').split(',')
    #             territory_name = territory.strip()
    #             num_troops = int(num_troops.strip())
    #             reasoning = reasoning.strip()
    #             return territory_name, num_troops, reasoning
    #         except (ValueError, IndexError) as e:
    #             print(f"Error parsing CSV response: {e}")
    #             return None, None, None
    #     else:
    #         try:
    #             territory, num_troops = response.strip('"').split(',')
    #             territory_name = territory.strip()
    #             num_troops = int(num_troops.strip())
    #             return territory_name, num_troops, None
    #         except (ValueError, IndexError) as e:
    #             print(f"Error parsing CSV response: {e}")
    #             return None, None, None
            
    def parse_response_text(
            self, move_response: Dict
        ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        response = move_response.choices[0].message.content
        print(f"Response content: {response}")

        # Regular expression to extract the move and reasoning
        move_match = re.search(r'\|\|\|(.+?),\s*(\d+)\|\|\|', response)
        reasoning_match = re.search(r'\+\+\+(.+?)\+\+\+', response)

        
        if move_match:
            territory_name = move_match.group(1).strip()
            num_troops = int(move_match.group(2).strip())
            
            # if not self.game_state.is_valid_territory(territory_name):
            #     print(f"Invalid territory: {territory_name}")
            #     return None, None, None
            
            reasoning = reasoning_match.group(1).strip() if reasoning_match else None
            
            return territory_name, num_troops, reasoning
        else:
            print(f"Error parsing response: {response}")
            return None, None, None

        
    def make_initial_troop_placement(
            self, game_state: 'GameState') -> str:
        # Implement strategy to make a move
        game_state_json = game_state.territories_df.to_json()

        player_territories = game_state.get_player_territories(self.name)

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
        The current game state is {game_state_json}. 
        You, are {self.name}, and you control the following territories: 
        {player_territories}. From the list of territories you control, and
        only from the list of territories you control, please suggest a 
        move. You can only place one troop. Think carefully
        about your move and consider also the moves of other players. 

        Your response should be in the following format:
        Move:|||Territory, Number of troops|||
        Reasoning:+++Reasoning for move+++

        For example:
        Move:|||Brazil, 1|||
        Reasoning:+++Brazil is a key territory in South America.+++

        Only provide the response in the specified format and please keep your 
        reasoning brief. And choose a territory you control, this is very 
        important for the grading of your submission.
        """


        # message_content_1 + message_content_2+ message_content_3

        parsed_response = (
            self.parse_response_text(
                self._send_message(
                 prompt))
        )

        return parsed_response
    

