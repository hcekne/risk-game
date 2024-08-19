import re
from typing import Dict,Optional,List,Tuple
from risk_game.llm_clients.llm_base import LLMClient

class PlayerAgent:
    def __init__(self, name: str, llm_client: LLMClient)-> None:
        self.name: str = name
        self.llm_client: LLMClient = llm_client
        self.include_reasoning: bool = True
        self.troops: int = 0
        self.turn_strategy: str = ""
        self.troop_placement_errors: int = 0
        self.return_formatting_errors: int = 0
        self.attack_errors: int = 0
        self.fortify_errors: int = 0
        self.card_trade_errors: int = 0
        self.accumulated_turn_time : float = 0.0
    
    def send_message(self, message_content: str) -> str:
        return self.llm_client.get_chat_completion(message_content)
    
    def parse_response_strategy(self, move_response: object) -> str:
        response = move_response.strip()
        response = response[:1200]
        return response

    def parse_response_text(
        self, move_response: object
    ) -> Tuple[List[Dict[str, int]], Optional[str], Optional[str]]:
        response = move_response.strip()
        # print(f"Response content: {response}")

        # Regular expression to extract all moves (e.g., |||Territory, 3|||)
        move_matches = re.findall(r'\|\|\|\s*(.+?)\s*,\s*(\d+)\s*\|\|\|', response)
        reasoning_match = re.search(r'\+\+\+\s*(.+?)\s*\+\+\+', response)
        from_territory_match = re.search(r'\#\#\#\s*(.+?)\s*\#\#\#', response)

        moves = []
        reasoning = None
        from_territory = None

        # print(f"move_matches: {move_matches}")  # Debugging print
        # print(f"reasoning_match: {reasoning_match}")  # Debugging print
        # print(f"from_territory_match: {from_territory_match}")  # Debugging print

        if move_matches:
            for match in move_matches:
                territory_name = match[0].strip()
                num_troops = int(match[1].strip())
                moves.append({
                    'territory_name': territory_name,
                    'num_troops': num_troops
                })

            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                reasoning = reasoning[:1200]

            if from_territory_match:
                from_territory = from_territory_match.group(1).strip()

            return moves, reasoning, from_territory
        else:
            response = response[:1200]
            print(f"------__------Error parsing response: ------__------" +
                  f"{response}")
            return [{'territory_name': None, 'num_troops': None}], None, None
        
    def parse_card_trade_response(
        self, move_response: object
    ) -> Tuple[Optional[List[int]], Optional[str]]:
        """
        Parses the player's response regarding card trade suggestions during the Risk card trade phase.
        
        Parameters:
        - move_response: The response object returned by the player agent (e.g., LLM).
        
        Returns:
        - A tuple where:
        - The first element is a list of card numbers to trade, or None if no trade is suggested.
        - The second element is an optional string containing reasoning, if provided.
        """
        response = move_response.strip()

        # Regular expression to extract card trade suggestions (e.g., ||| 1, 3, 4 |||)
        trade_match = re.search(r'\|\|\|\s*(0|(?:\d+(?:\s*,\s*\d+)*))\s*\|\|\|', response)
        
        # Optional reasoning extraction (if any)
        reasoning_match = re.search(r'\+\+\+\s*(.+?)\s*\+\+\+', response)
        
        trade_cards = None
        reasoning = None

        # Check if a trade suggestion was found
        if trade_match:
            card_numbers = trade_match.group(1)
            trade_cards = [int(num.strip()) for num in card_numbers.split(',')]
        
            # Extract reasoning, if provided
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                reasoning = reasoning[:1200]

            return trade_cards, reasoning
        else:
            response = response[:1200]
            print(f"------__------Error parsing response: ------__------" +
                  f"{response}")
            return trade_cards, reasoning
        
    def format_list_of_cards(self, cards: List['Card']) -> str:
        # Step 1: Convert the list of cards into a formatted string
        list_of_cards = ""
        for index, card in enumerate(cards, start=1):
            list_of_cards += f"{index}. {card.territory} {card.troop_type}\n"
        return list_of_cards
  
    def format_valid_combinations(self, 
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]) -> str:
        formatted_combinations = ""
        
        for value, combinations in valid_combinations.items():
            for combination, wildcard_used in combinations:
                wildcard_text = "Wildcard used" if wildcard_used else "Wildcard not used"
                formatted_combinations += f"{value} troops: {combination} ({wildcard_text})\n"
        
        return formatted_combinations
        
        
    def make_initial_troop_placement(
            self, game_state: 'GameState', error_msg: Optional[str] = None
    ) -> str:
        # Implement strategy to make a move
        current_game_state = game_state.format_game_state()
        player_territories = game_state.get_player_territories(self.name)
        prompt = f"""
        We are playing Risk and we are in the initial troop placement phase.
        You, are {self.name}, and it is your turn. 
        """
        if error_msg:
             prompt += (f"Your last move was invalid:\n {error_msg} \nPlease " +
             f"try again and DON'T make the same mistake.\n")


        prompt += f"""
        {current_game_state}

        From territories you control, and ONLY from one of the territories 
        you control, please suggest a move. You can only place one troop. 
        Think carefully about your move and consider also the moves of other players. 

        Your response should be in the following format:
        Move:|||Territory, Number of troops|||
        Reasoning:+++Reasoning for move+++

        For example:
        Move:|||Brazil, 1|||
        Reasoning:+++Brazil is a key territory in South America.+++

        Only provide the response in the specified format and please keep your 
        reasoning very brief. And you must remebmer to choose a territory 
        you control, this is very important for the grading of your submission.
        """
        parsed_response = (
            self.parse_response_text(
                self.send_message(
                 prompt))
        )
        return parsed_response
    

    def make_troop_placement(
            self, game_state: 'GameState',  error_msg: Optional[str] = None
    ) -> str:
        current_game_state = game_state.format_game_state()
        player_territories = game_state.get_player_territories(self.name)

        prompt = f"""
        We are playing Risk and we are in the troop placement phase.
        You, are {self.name}, and it is your turn. 
        """
        if error_msg:
             prompt += (f"Your last move was invalid:\n {error_msg} \nPlease " +
             f"try again and DON'T make the same mistake.\n")


        prompt += f"""
        {current_game_state}

        From territories you control, and ONLY from one of the territories 
        you control, please suggest your moves. You can place troops on any 
        of the territories you control, and you must place the 
        number of available troops. You have {self.troops} to place. 
        Think carefully about your move and consider also the moves of 
        other players. 

        Your response should be in the following format:

        Move 1: |||Territory, Number of troops|||

        Move 2: |||Territory, Number of troops|||

        Move 3: |||Territory, Number of troops|||

        For as many moves as you need to place all your troops.

        Reasoning:+++Reasoning for move+++

        For example:

        Move 1: |||Brazil, 1|||

        Move 2: |||Argentina, 2|||

        Move 3: |||Peru, 4|||

        Reasoning: +++Brazil, Argentina and Peru are key in South America+++

        Only provide the response in the specified format and please keep your 
        reasoning very brief. And remember you must choose territories you
        control, this is very important for the grading of your submission!
        """
        parsed_response = (
            self.parse_response_text(
                self.send_message(
                 prompt))
        )

        return parsed_response
    
    def make_fortify_move(
            self, game_state: 'GameState', error_msg: Optional[str] = None
    ) -> str:
        # Implement strategy to make a move
        current_game_state = game_state.format_game_state()
        strong_territories = game_state.get_strong_territories(self.name)
        territories_with_troops  = (
            game_state.get_strong_territories_with_troops(self.name))


        prompt = f"""
        We are playing Risk and we are in the troop fortify phase.
        You, are {self.name}, and it is your turn. 

        """

        if error_msg:
             prompt += (f"Your last move was invalid:\n {error_msg} \nPlease " +
             f"try again and DON'T make the same mistake.\n")


        prompt += f"""
        {current_game_state}

        Your current strategy for this turn is: {self.turn_strategy}

        **Objective:**
        Your goal is to fortify your borders by moving large numbers of 
        troops to the key border territories that you control. This will 
        allow you to launch powerful attacks in the next round. Do not 
        waste time with small, incremental fortifications. Focus on 
        concentrating your forces in preparation for a decisive attack.

         **Strategic Considerations:**
        - Identify your key border territories, especially those that are 
        adjacent to enemy territories.
        - Move a significant number of troops to these key border 
        territories to strengthen your defenses and prepare for a major offensive in the next round.
        - Avoid spreading your troops too thin. Focus on fortifying with large numbers of troops, rather than just small reinforcements.

        To choose a territory to fortify from, you need to have more than one 
        troop in that territory. The territories you have more than 
        one troop in are: {strong_territories}.
        To fortify is optional and you can choose not to fortify.

        If you choose to fortify, choose a territory ONLY from the following
        list of tuples containing territories and troop numbers:
        {territories_with_troops}. The troop number indicates the maximum
        numer of troops you can move from that territory.

        Also, most importantly, you MUST fortify between two territories 
        that are connected by a chain of territories under your control.

        To Territory:|||To Territory, Number of troops|||
        From Territory: ### From Territory ###
        Reasoning:+++Reasoning for move+++

        For example:
        To Territory:|||Brazil, 10|||
        From Territory:###Argentina###

        Reasoning:+++I need more troops in Brazil+++

        If you don't want to fortify, you can provide the following response:
        To Territory:|||Blank, 0|||
        From Territory:###Blank###
        Reasoning:+++I don't want to fortify+++

        Only provide the response in the specified format and please keep your 
        reasoning brief, this is very important for the grading of your 
        submission.
        """
        parsed_response = (
            self.parse_response_text(
                self.send_message(
                 prompt))
        )

        return parsed_response

    def make_attack_move(
            self, game_state: 'GameState', successful_attacks: int, 
            error_msg: Optional[str] = None
    ) -> str:
        # Implement strategy to make an attack
        current_game_state = game_state.format_game_state()
        strong_territories = (
            game_state.get_strong_territories_with_troops(self.name))
        
        possible_attack_vectors = (
            game_state.get_adjacent_enemy_territories(
                self.name, strong_territories))
        
        formatted_attack_vectors = (
            game_state.format_adjacent_enemy_territories(possible_attack_vectors))

        prompt = f"""
        We are playing Risk and we are in the attack phase.   
        You, are {self.name}, and it is your turn. 

        We are playing global domination, and you are trying to take over the world.
        You need to capture all the territories and elimnation all the other
        players to win the game.

        """

        if error_msg:
             prompt += (f"Your last move was invalid:\n {error_msg} \nPlease " +
             f"try again and DON'T make the same mistake.\n")


        prompt += f"""
        {current_game_state}

        You have had {successful_attacks} successful attacks so far. 

        Your current strategy for this turn is: {self.turn_strategy}

        {formatted_attack_vectors} 

        Your attack MUST be chosen using one of the options from the list 
        above. (you can chose to attack with less troops than the maximum 
        number of troops in the dictionary).

        PRO TIP: When attacking, it is always a good idea to attack with 3 or 
        more troops, because you will have a higher chance of winning the 
        attack. This is because the defender always wins if the dice rolls are 
        equal.

        Remember, to attack is optional and you can choose not to attack. 
        however, if you don't have any successful attacks, you will not 
        receive a card.

        Your response MUST be in the following format:

        Attack Opponent Territory:||| Territory, Number of troops|||
        From Territory: ### From Territory ###
        Reasoning:+++Reasoning for move+++

        For example:
        Attack Opponent Territory:|||Brazil, 3|||
        From Territory:###Argentina###

        Reasoning:+++I want to attack Brazil with 3 troops from Argentina
        because it will help give me control over South America+++

        When you are finished attacking, or don't want to attack this turn,
        you can provide the following response:

        Attack Opponent Territory:|||Blank, 0|||
        From Territory:###Blank###
        Reasoning:+++I am finished attacking because I don't want to overextend+++

        Only provide the response in the specified format and please keep your 
        reasoning brief, this is very important for the grading of your 
        submission.
        """
        # print(f"---------------This is the attack prompt:----------------")
        # print(prompt)
        parsed_response = (
            self.parse_response_text(
                self.send_message(
                 prompt))
        )

        return parsed_response

    
    def must_trade_cards(self, cards: List['Card'], game_state: 'GameState',
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]
        ) -> Tuple[Optional[List[int]], Optional[str]]:

        formatted_valid_combinations = self.format_valid_combinations(
            valid_combinations)

        list_of_cards = self.format_list_of_cards(cards)        
        
        prompt = f"""
        You are playing Risk and are currently in the card trade phase. 
        The following is a list of cards you have:

        {list_of_cards}

        The following is a list of valid card combinations, the first number
        is the number of troops you will receive for trading in the cards

        {formatted_valid_combinations}

        You can only choose a combination from the above list of valid 
        card combinations.

        Instructions:

        Objective: Your goal is to decide which set of cards to trade in for 
        troops. You have 5 or more cards and need to trade cards.

        Rules:

        Valid Sets:

        Three of a Kind: Three cards of the same type (e.g., three Infantry cards).

        One of Each Type: One Infantry, one Cavalry, and one Artillery card.

        Wild Cards (if available) can substitute for any type of card.

        Response Format:

        Plase espond with the list of card numbers in the format:

        List of cards to trade ||| [Card Numbers] |||

        Example:
        List of cards to trade ||| 1, 3, 4 |||

        """
        # print(f"-----------This is the must trade cards prompt:---------------")
        # print(prompt)   
        parsed_response = (
            self.parse_card_trade_response(
                self.send_message(
                 prompt))
        )

        return parsed_response
    

    def may_trade_cards(self, cards: List['Card'], game_state: 'GameState',
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]
        ) -> Tuple[Optional[List[int]], Optional[str]]:
        
        current_game_state = game_state.format_game_state()
        formatted_valid_combinations = self.format_valid_combinations(
            valid_combinations)

        list_of_cards = self.format_list_of_cards(cards)       
        
        prompt = f"""
        You are playing Risk and are currently in the card trade phase. 
        The following is a list of cards you have:

        {list_of_cards}

        Instructions:

        Objective: Your goal is to decide whether to trade in a set of three 
        cards or to hold onto your cards for future turns.

        Rules:

        Valid Sets:

        Three of a Kind: Three cards of the same type (e.g., three Infantry cards).

        One of Each Type: One Infantry, one Cavalry, and one Artillery card.

        Wild Cards (if available) can substitute for any type of card.

        The following is a list of valid card combinations, the first number
        is the number of troops you will receive for trading in the cards

        {formatted_valid_combinations}

        You can ONLY choose a combination from the above list of valid 
        card combinations.

        Strategy Considerations:

        Maximize Troop Gain: Trading in a set of cards will provide you with 
        additional troops. Consider whether the trade will significantly 
        strengthen your position.

        Hold for Later: Sometimes it may be better to hold onto your cards to 
        create a stronger set in future turns, especially if you are not in 
        immediate need of additional troops.

        Opponent Awareness: Consider the state of your opponents. 
        If they are weak or you have a strategic advantage, it might be 
        worth trading in cards to press your advantage. Conversely, 
        if you are in a strong position, holding cards for later might 
        be more beneficial.

        Response Format:

        If you decide to trade in a set of cards, respond with the list of 
        card numbers in the format:

        List of cards to trade ||| Card Numbers (separated by commas) |||

        Example:
        List of cards to trade ||| 1, 3, 4 |||

        If you decide not to trade any cards, respond with:
        ||| 0 |||

        """

        # print(f"-----------This is the may trade cards prompt:---------------")
        # print(prompt)   

        parsed_response = (
            self.parse_card_trade_response(
                self.send_message(
                 prompt))
        )

        return parsed_response
        
    
    def choose_capital(self, game_state: 'GameState') -> str:
        # Implement strategy to choose a capital
        # return the name of the capital
        pass

    def define_strategy_for_move(self, game_state: 'GameState') -> None:
        # Implement strategy to make a move
        strong_territories = (
            game_state.get_strong_territories_with_troops(self.name))
        
        possible_attack_vectors = (
            game_state.get_adjacent_enemy_territories(
                self.name, strong_territories))
        
        formatted_attack_vectors = (
            game_state.format_adjacent_enemy_territories(possible_attack_vectors))


        prompt = """
        We are playing Risk, World Domination.
        You, are {self.name}, and it is your turn.

        {current_game_state}

        {formatted_attack_vectors}

        Your task is to formulate an overall strategy for your turn, 
        considering the territories you control, the other players, and the 
        potential for continent bonuses.

        **Objective:**

       Your goal is to win the game by eliminating all opponents and 
       controlling the entire map. Focus on decisive attacks that reduce 
       your opponents' ability to fight back. When possible, eliminate 
       opponents to gain their cards, which will allow you to trade them 
       in for more troops and accelerate your conquest.


        **Strategic Considerations:**

        1. **Attack Strategy:**
        - Identify the most advantageous territories to attack.
        - Prioritize attacks that will help you secure continent bonuses or 
        weaken your strongest opponents.
        - Look for opportunities to eliminate other players. If an opponent 
        has few territories left, eliminating them could allow you to gain 
        their cards, which can be especially powerful if you’re playing with 
        progressive card bonuses.
        - Weigh the risks of attacking versus the potential rewards.

        2. **Defense Strategy:**
        - Identify your most vulnerable territories and consider fortifying them.
        - Consider the potential moves of your opponents and plan your defense 
        accordingly.

        Multi-Turn Planning: Think about how you can win the game within 
        the next 2-3 turns. What moves will set you up for a decisive victory?
        Don't just focus on this turn; consider how your actions this turn 
        will help you dominate in the next few turns.


        **Instructions:**

        - **Limit your response to a maximum of 300 words.**
        - **Be concise and direct. Avoid unnecessary elaboration.**
        - **Provide your strategy in two bullet points, each with a maximum of four sentences.**

        **Output Format:**

        Provide a high-level strategy for your turn, including:
        1. **Attack Strategy:** Which territories will you target, and why? 
        How many troops will you commit to each attack? If you plan to 
        eliminate an opponent, explain how you will accomplish this.
        2. **Defense Strategy:** Which territories will you fortify, and 
        how will you allocate your remaining troops?

        Example Strategy:
        - **Attack Strategy:** Attack {Territory B} from {Territory C} with 
        10 troops to weaken Player 1 and prevent them from securing the 
        continent bonus for {Continent Y}. Eliminate Player 2 by attacking 
        their last remaining territory, {Territory D}, to gain their cards.
        - **Defense Strategy:** Fortify {Territory E} with 3 troops to 
        protect against a potential counter-attack from Player 3.

        Remember, your goal is to make the best strategic decisions that
            will maximize your chances of winning the game. Consider the 
            potential moves of your opponents and how you can position 
            yourself to counter them effectively.

        What is your strategy for this turn?
        """
        parsed_response = (
            self.parse_response_strategy(
                self.send_message(
                 prompt))
        )
        

        self.turn_strategy = parsed_response

def choose_capital(self, game_state: 'GameState') -> str:
    # Implement strategy to choose a capital
    # return the name of the capital
    pass