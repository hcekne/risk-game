from typing import Dict, List, Optional, Tuple
import random
from risk_game.player_agent import PlayerAgent
from risk_game.game_state import GameState
from risk_game.rules import Rules
from risk_game.card_deck import Deck, Card

class GameMaster:
    def __init__(self, rules: Rules)-> None:
        self.players: List[PlayerAgent] = []
        self.dead_players: List[PlayerAgent] = []
        self.active_players: List[PlayerAgent] = []
        self.game_state = None
        self.game_round = 0
        self.phase: int = 0
        self.rules = Rules()
        self.current_player_index = -1
        self.deck = None
        self.winner: Optional[PlayerAgent] = None
        self.discarded_cards = []
        self.rules = rules  # Store the rules instance
        self.trade_count = 0  # Track the number of trades for progressive mode
        self.player_cards: Dict[str, List[Card]] = {}

    def add_player(self, name:str, model_number:int) -> None:
        if len(self.players) >= 6:
            raise ValueError("Cannot add more than 6 players")
        player = PlayerAgent(name, model_number)
        self.players.append(player)
        self.player_cards[name] = []  # Initialize an empty list of cards 

    def calculate_initial_troops(self, num_players: int) -> int:
        initial_troops_map = {2: 40,3: 35, 4: 30,5: 25,6: 20}
        return initial_troops_map[num_players]

    def init_game_state(self) -> None:
        num_players = len(self.players)
        # only init the game state if there are 2 or more players
        if num_players < 2:
            raise ValueError("Cannot start a game with fewer than 2 players")
        random.shuffle(self.players)
        intial_troops = self.calculate_initial_troops(num_players)
        for player in self.players:
            player.troops = intial_troops
        self.active_players = self.players.copy()
        self.game_state = GameState(self.active_players)
        self.deck = Deck()

    def remove_player(self, player_name: str) -> None:
        player_to_remove = None
        remove_index = -1
        for i, player in enumerate(self.active_players):
            if player.name == player_name:
                player_to_remove = player
                remove_index = i
                break
        print(f"Index of Player to remove: {remove_index}")

        if player_to_remove:
            self.active_players.remove(player_to_remove)
            self.dead_players.append(player_to_remove)
            self.game_state.num_players = len(self.active_players)
            # Adjust current_player_index based on the removed player's position
            if remove_index < self.current_player_index:
                self.current_player_index -= 1
            elif remove_index == self.current_player_index:
                self.current_player_index = (
                    self.current_player_index % len(self.active_players)
                )
            # Reset current_player_index if it goes out of bounds
            if self.current_player_index >= len(self.active_players):
                self.current_player_index = 0
        else:
            print(f"{player_name} not found in active players")

    def list_players(self) -> None:
        for player in self.players:
            print(f"Name: {player.name}")

    def validate_single_move(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
        ) -> bool:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        print(f"Territory: {territory}, Num troops: {num_troops}")
        if territory is None or num_troops is None:
            print(f"Error: Territory or num_troops is None")
            player.return_formatting_errors += 1
            return False
        if not self.game_state.check_terr_control(player.name, territory):
            print(f"Error: {player.name} does not control territory {territory}")
            player.troop_placement_errors += 1
            return False
        if num_troops > player.troops:
            print(f'''
                  Error: Not enough troops to place. {player.name} has only 
                  {player.troops} troop(s) left.'''
            )
            player.troop_placement_errors += 1
            return False
        return True

    def update_current_player_index(self):
        self.current_player_index = (
            (self.current_player_index + 1) % len(self.active_players)
        )
    
    def distribute_territories_random(self) -> int:
        if not self.game_state:
            raise ValueError("Game state is not initialized")
        self.current_player_index = (
            self.game_state.assign_territories_to_players_random(self.active_players))
        return self.current_player_index
    
    def choose_capitals(self) -> None:
        if self.rules.capitals: 
            for player in self.active_players:
                while player.capital is None:
                    capital = player.choose_capital(self.game_state)
                    player.capital = capital
                
    def initial_troop_placement(self):
        #self.current_player_index = 0
        while any(player.troops > 0 for player in self.active_players):
            current_player = self.active_players[self.current_player_index]
            print(f"*****-------------NOW PLACING TROOPS FOR: -------------*****")
            print(f"Current player name: {current_player.name}")
            if current_player.troops > 0:
                self.ensure_valid_move(current_player)
            # Move to the next player
            self.current_player_index = (
                (self.current_player_index + 1) % len(self.active_players)
            )
        print("Initial troop placement complete")

    def play_a_turn(self, player: 'PlayerAgent')-> None:
        print(f"---------Player {player.name} is starting their turn.----------")
        # Phase 1: Troop Placement
        self.phase_1_troop_placement(player)
        self.phase_2_attack(player)
        self.phase_3_fortify(player)
        print(f"{player.name} has completed their turn.")
        # Phase 2: Attack
        # Phase 3: Fortify

    def force_trade_in_cards(self, player: 'PlayerAgent') -> None:
        player_cards = self.player_cards.get(player.name)
        valid_combinations = self.rules.find_valid_combinations(
            player_cards,player.name, self.game_state)
        # Make the player propose a trade
        cards_to_trade, _ = player.must_trade_cards(player_cards,
            self.game_state, valid_combinations)
        
        if cards_to_trade is None:
            print(f"{player.name} failed to provide valid response to cards.")
            return
        else:
            print(cards_to_trade)
            cards_to_trade
            selected_cards = [player_cards[i - 1] for i in cards_to_trade]
            # Verify the proposed trade using the rules instance
            print(selected_cards)
        
            valid, troops, _ = self.rules.verify_card_combination(
                selected_cards, player.name, self.game_state)

            if valid:
                # Remove the traded cards from the player's hand
                for card in selected_cards:
                    player_cards.remove(card)
                    self.discarded_cards.append(card)

                # Grant the player the corresponding troops
                player.troops += troops
                print(f"{player.name} traded in cards for {troops} extra troops.")
            else:
                print(f"Invalid trade attempt by {player.name}.")


    def ask_to_trade_in_cards(self, player: 'PlayerAgent') -> None:
        player_cards = self.player_cards.get(player.name)
        # Ask the player if they want to trade in cards
        valid_combinations = self.rules.find_valid_combinations(
            player_cards, player.name, self.game_state)
        cards_to_trade, _ = player.may_trade_cards(player_cards, 
            self.game_state, valid_combinations)
        
        if cards_to_trade is None:
            print(f"{player.name} failed to provide valid response to cards.")
            return

        if cards_to_trade.pop() == 0:
            print(f"{player.name} chose not to trade in cards.")
            return
        else:
            print(cards_to_trade)
            selected_cards = [player_cards[i - 1] for i in cards_to_trade]
            # Verify the proposed trade using the rules instance
            valid, troops, _ = self.rules.verify_card_combination(
                selected_cards,player.name, self.game_state)

            if valid:
                # Remove the traded cards from the player's hand
                for card in selected_cards:
                    player_cards.remove(card)
                    self.discarded_cards.append(card)

                # Grant the player the corresponding troops
                player.troops += troops
                print(f"{player.name} traded in cards for {troops} extra troops.")
            else:
                print(f"Invalid trade attempt by {player.name}.")

    def phase_1_troop_placement(self, player: 'PlayerAgent')-> None:
        self.phase = 1
        player.troops = 0
        # Make the player define a strategy for the turn
        player.define_strategy_for_move(self.game_state)

        # figure out if the player needs to trade in cards (i.e. has 5 or more cards)
        while len(self.player_cards[player.name]) >= 5:
            self.force_trade_in_cards(player)
        
        if (len(self.player_cards[player.name]) >= 3):
            # check if the player has a set of cards that can be traded in
            if self.rules.has_valid_combination(self.player_cards[player.name]):
                 self.ask_to_trade_in_cards(player)

        # figure out how many troops the player gets
        total_troops_from_territories = self.rules.calculate_troops(
            self.game_state.get_player_territories(player.name),self.game_state)
        
        player.troops += total_troops_from_territories
        # ensure the player places all their troops on the board
        self.ensure_valid_move(player)

        # end phase 1

    def phase_2_attack(self, player: 'PlayerAgent')-> None:
        self.phase = 2
        print(f"{player.name} is attacking")
    
        successful_attacks = self.ensure_valid_attack_move(player)
        if successful_attacks > 0:  # Player gets a card if they won an attack
            card = self.deck.draw_card(self.discarded_cards)
            self.player_cards[player.name].append(card)
            print(f"{player.name} won an attack and received a card")


    def phase_3_fortify(self, player: 'PlayerAgent') -> None:
        self.phase = 3
        print(f"{player.name} is fortifying")
        self.ensure_valid_fortify_move(player)

    def is_game_over(self) -> bool:
        if self.rules.capitals:
            # Check if any player controls all capitals
            for player in self.players:
                player_territories = (
                    self.game_state.get_player_territories(player.name))
                if all(capital in player_territories for 
                       capital in self.game_state.capitals.values()):
                    return True  # This player controls all capitals, game over
        else:
            # Check if any player controls all territories
            for player in self.players:
                player_territories = (
                    self.game_state.get_player_territories(player.name))
                if len(player_territories) == len(self.game_state.territories_df):
                    return True  # This player controls all territories, game over

        return False  # No victory condition met, game continues

    def play_game(self) -> None:
        while not self.is_game_over():
            if self.game_round > self.rules.max_rounds:
                print("Game over: Maximum rounds reached")
                break
            self.game_round += 1
            # remove any players with no territories
            # first create a list of players to remove
            # iteratate through list and remove players
            
            print(f'Starting round: {self.game_round}')
            print(f'This is the current game state:----------')
            print(self.game_state.territories_df)
            for player in self.active_players:
                # distribute some cards to test logic needs to be taken out
                if self.game_round == 1:
                    for _ in range(5):
                        card = self.deck.draw_card(self.discarded_cards)
                        self.player_cards[player.name].append(card)
                self.play_a_turn(player)
                # check if the game is over
                if self.is_game_over():
                    self.winner = player
                    break


        print("Game over")
        if self.game_round > self.rules.max_rounds:
            print(f"No winner after {self.rules.max_rounds} rounds")
        else:
            print(f"{self.winner.name} wins")
        print(f"Game lasted {self.game_round} rounds")


    def validate_move(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        total_troops = 0

        for move in moves:
            territory = move.get('territory_name')
            num_troops = move.get('num_troops')
            
            #print(f'''Validating move: Territory: {territory}, 
            #      Num troops: {num_troops}''')

            if territory is None or num_troops is None:
                error_msg = f"Error: Territory or num_troops is None"
                print(error_msg)
                return False, error_msg

            if not self.game_state.check_terr_control(player.name, territory):
                error_msg = (f"Error: {player.name} does not control territory " +
                            f"{territory}")
                print(error_msg)
                return False, error_msg

            total_troops += num_troops

        if total_troops > player.troops:
            error_msg = (
            f"Error: Not enough troops to place. {player.name} has only " + 
            f"{player.troops} troop(s) left but trying to place {total_troops}.")
            print(error_msg)
            return False, error_msg

        if total_troops < player.troops:
            error_msg = (
            f"Error: Not placing all troops. {player.name} is trying to place " +
            f"{total_troops} troop(s) but has {player.troops}.")
            print(error_msg)
            return False, error_msg

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid

    def ensure_valid_move(
        self, player: 'PlayerAgent')-> None:
        valid_move = False
        invalid_moves = 0
        erro_msg = None

        while not valid_move:
            if self.phase == 0:
                # Phase 0: Initial troop placement 
                # (single move treated as a list with one move)
                moves, reasoning, _  = (
                    player.make_initial_troop_placement(self.game_state, erro_msg))
            elif self.phase == 1:
                # Phase 1: Troop placement (multiple moves)
                moves, reasoning, _ = (
                    player.make_troop_placement(self.game_state, erro_msg))
            else:
                raise ValueError(f"Unknown phase: {self.phase}")
            
            # Validate the moves
            is_valid, error_msg = self.validate_move(player, moves, reasoning)

            if is_valid:
                print("Moves are valid")
                self.update_game_state_for_multiple_moves(player, moves)
                self.reduce_player_troops_for_multiple_moves(player, moves)
                valid_move = True
            elif invalid_moves >= 3:
                print("Too many invalid moves, random troop placement turn")
                moves = self.generate_random_troop_placementplayer(
                    player, self.game_state) 
                reasoning = "Random troop placement"

                is_valid, error_msg = self.validate_move(player, moves, reasoning)

                if self.validate_move(player, moves, reasoning):
                    print("Random moves are valid")
                    self.update_game_state_for_multiple_moves(player, moves)
                    self.reduce_player_troops_for_multiple_moves(player, moves)
                    valid_move = True
                else:
                    raise ValueError("Random troop placement failed")
                
            else:
                print(f"Moves are invalid: {error_msg}, asking for new moves")
                invalid_moves += 1

    def ensure_valid_fortify_move(
        self, player: 'PlayerAgent')-> None:
        fortify_tries = 0
        error_msg = None

        while fortify_tries < 3:
            moves, reasoning, from_territory = (
                player.make_fortify_move(self.game_state, error_msg)
            ) 
            # print(f"Proposed moves: {moves}, Reasoning: {reasoning}")
            is_valid, error_msg = self.validate_fortify_move(
                player, moves, reasoning, from_territory)

            if is_valid:
                print("Moves are valid")
                self.update_game_state_for_fortify_move(
                    player, moves, from_territory)
                fortify_tries = 4  # Exit the loop
            else:
                print(f"Moves are invalid,\n{error_msg}\n Asking for new moves")
                fortify_tries += 1
    
    def validate_fortify_move(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
       
        territory = moves[0].get('territory_name')
        num_troops = moves[0].get('num_troops')

        if territory is None or num_troops is None:
            error_msg = f"Error: Territory or num_troops is None"
            print(error_msg)
            return False, error_msg
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not fortify")
            return True, None  # Blank move is valid

        if not self.game_state.check_terr_control(
            player.name, territory):
            error_msg = (f"Error: {player.name} does not control to " +
                    f"territory {territory}")
            print(error_msg)
            return False ,error_msg
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            error_msg = (f"Error: {player.name} does not control from " +
                    f"territory {territory}")
            print(error_msg)
            return False ,error_msg
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            error_msg = (f"Error: Not enough troops to fortify. {player.name} " +
            f"has only {from_territory_troops} troop(s) in {from_territory} " +
            f"but trying to move {num_troops}.")
            print(error_msg)
            return False ,error_msg
        
        # Check if the territories are connected
        if not self.game_state.are_territories_connected(
            player.name, from_territory, territory):
            error_msg = f"Error: Territories are not connected"
            print(error_msg)
            return False ,error_msg

        # Optionally handle reasoning here
        if reasoning:
            print(f"Reasoning: {reasoning}")

        return True, None  # All moves are valid
    
    def update_game_state_for_fortify_move(
        self, player: 'PlayerAgent', moves: List[Dict[str, int]],
        from_territory: str)-> None:
        for move in moves:
            territory = move['territory_name']
            num_troops = move['num_troops']
            if territory == 'Blank' or num_troops == 0:
                return
            # update troops for the to_territory
            self.game_state.update_troops(player.name, territory, num_troops)
            #update the troops for the from_territory
            self.game_state.update_troops(player.name, from_territory, -num_troops)


    def update_game_state_for_multiple_moves(
            self, player: 'PlayerAgent', moves: List[Dict[str, int]])-> None:
        # Iterate over each move and apply it to the game state
        for move in moves:
            territory = move['territory_name']
            num_troops = move['num_troops']
            # Update the game state (for example, add troops to the territory)
            self.game_state.update_troops(player.name, territory, num_troops)

    def reduce_player_troops_for_multiple_moves(
            self, player: 'PlayerAgent', moves: List[Dict[str, int]])-> None:
        # Reduce the player's troop count based on the total troops placed
        total_troops = sum(move['num_troops'] for move in moves)
        player.troops -= total_troops

    def ensure_valid_attack_move(
        self, player: 'PlayerAgent')-> int:
        invalid_attacks = 0
        lost_attacks = 0
        successful_attacks = 0
        error_msg = None

        while invalid_attacks < 3:
            move, reasoning, from_territory = (
                player.make_attack_move(self.game_state, successful_attacks, 
                                        error_msg)
            ) 
            # print(f"Proposed attack: {move} from {from_territory}, " +
            #       f"Reasoning: {reasoning}")
            
            is_valid, error_msg = self.validate_attack_move(
                player, move, reasoning, from_territory)

            if is_valid:
                print("Moves are valid")
                # calculate the outcome of the attack
                outcome = self.game_state.update_game_state_for_attack_move(
                    player, move, from_territory)
                if outcome == 'no_attack':
                    print("No attack was made")
                    invalid_attacks = 4  # Exit the loop
                elif outcome == 'win':
                    successful_attacks += 1
                    print("Player won the attack")
                else:
                    print("Player lost the attack")
                    lost_attacks += 1
                
            else:
                invalid_attacks += 1
                print(f"Moves are invalid:\n{error_msg}\nAsking for new moves")
        return successful_attacks

    def validate_attack_move(
        self, player: 'PlayerAgent', 
        move: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:    
        total_troops = 0
       
        territory = move[0].get('territory_name')
        num_troops = move[0].get('num_troops')
        
        #print(f'''Validating move: Territory: {territory}, 
        #        Num troops: {num_troops}''')

        if territory is None or num_troops is None:
            error_msg = f"Error: Territory or num_troops is None"
            print(error_msg)
            return False, error_msg
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not attack!!")
            return True, None  # Blank move is valid

        if self.game_state.check_terr_control(
            player.name, territory):
            error_msg = (f"Error: {player.name} already controls " +
                  f"territory {territory}")
            print(error_msg)
            return False, error_msg
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            error_msg = (f"Error: {player.name} does not control from " +
                f"territory {territory}")
            print(error_msg)
            return False, error_msg
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            error_msg = (f"Error: Not enough troops to Attack. {player.name} " +
            f"has only {from_territory_troops} troop(s) in {from_territory} " +
            f"but trying to attack with {num_troops}.")
            print(error_msg)
            return False, error_msg
        
        # Check if the territories are adjacent
        if not self.game_state.check_if_adjacent(from_territory, territory):
            error_msg = f"Error: Territories are not connected"
            print(error_msg)
            return False, error_msg

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True, None  # All moves are valid

    def generate_random_troop_placement(self, player: 'PlayerAgent', 
        game_state: 'GameState'
    ) -> List[Dict[str, int]]:
        """
        Generates a random troop placement for a player. The function will randomly
        distribute the player's available troops across the territories they control.

        Parameters:
        - player: The player for whom to generate the move.
        - game_state: The current state of the game.

        Returns:
        - A list of dictionaries representing the troop placement move. 
        Each dictionary contains a territory name and the number of troops placed there.
        """

        # Get the list of territories the player controls
        controlled_territories = game_state.get_player_controlled_territories(player.name)

        # Total troops to allocate
        troops_to_allocate = player.troops

        # Initialize an empty list to store the troop placement moves
        troop_placement = []

        # Randomly distribute troops among controlled territories
        for territory in controlled_territories:
            if troops_to_allocate <= 0:
                break

            # Randomly decide the number of troops to place in the current territory
            troops_for_this_territory = random.randint(1, troops_to_allocate)
            troop_placement.append({'territory_name': territory, 'num_troops': troops_for_this_territory})

            # Subtract the allocated troops from the total remaining troops
            troops_to_allocate -= troops_for_this_territory

        # If there are still troops remaining, distribute them across the territories randomly
        while troops_to_allocate > 0:
            for move in troop_placement:
                if troops_to_allocate <= 0:
                    break
                move['num_troops'] += 1
                troops_to_allocate -= 1

        return troop_placement
        
