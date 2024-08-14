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
            return False
        if not self.game_state.check_terr_control(player.name, territory):
            print(f"Error: {player.name} does not control territory {territory}")
            return False
        if num_troops > player.troops:
            print(f'''
                  Error: Not enough troops to place. {player.name} has only 
                  {player.troops} troop(s) left.'''
            )
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

    def trade_in_cards(self, player: 'PlayerAgent') -> None:
        player_cards = self.player_cards[player.name]
        game_state = self.game_state

        # Ask the player to propose a trade
        cards_to_trade = player.propose_trade(player_cards, game_state)

        # Verify the proposed trade using the rules instance
        valid, troops = self.rules.verify_card_combination(cards_to_trade)
        if valid:
            # Remove the traded cards from the player's hand
            for card in cards_to_trade:
                player_cards.remove(card)
                self.discarded_card(card)

            # Grant the player the corresponding troops
            player.troops += troops
            print(f"{player.name} traded in cards for {troops} extra troops.")
        else:
            print(f"Invalid trade attempt by {player.name}.")

    def phase_1_troop_placement(self, player: 'PlayerAgent')-> None:
        self.phase = 1
        player.troops = 0
        # figure out if the player needs to trade in cards (i.e. has 5 or more cards)

        while len(self.player_cards[player.name]) >= 5:
            self.trade_in_cards(player)
        
        if (len(self.player_cards[player.name]) >= 3):
            # check if the player has a set of cards that can be traded in
            if self.rules.has_valid_combination(self.player_cards[player.name]):

            # ask the player if they want to trade in cards and if so trade the 
                if player.agree_to_trade(self.game_state):
                    self.trade_in_cards(player)

        # figure out how many troops the player gets
        total_troops_from_territories = self.rules.calculate_troops(
            self.game_state.get_player_territories(player.name),self.game_state)
        
        player.troops += total_troops_from_territories
        # ensure the player places all their troops on the board
        self.ensure_valid_move(player)

        # end phase 1
        pass

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
    ) -> bool:
        total_troops = 0

        for move in moves:
            territory = move.get('territory_name')
            num_troops = move.get('num_troops')
            
            #print(f'''Validating move: Territory: {territory}, 
            #      Num troops: {num_troops}''')

            if territory is None or num_troops is None:
                print("Error: Territory or num_troops is None")
                return False

            if not self.game_state.check_terr_control(player.name, territory):
                print(f"Error: {player.name} does not control territory {territory}")
                return False

            total_troops += num_troops

        if total_troops > player.troops:
            print(f'''
            Error: Not enough troops to place. {player.name} has only 
            {player.troops} troop(s) left but trying to place {total_troops}.'''
            )
            return False

        if total_troops < player.troops:
            print(f'''
            Error: Not placing all troops. {player.name} is trying to place
            {total_troops} troop(s) but has  {player.troops}.'''
            )
            return False

        # Optionally handle reasoning here
        if reasoning:
            # print(f"Reasoning: {reasoning}")
            pass

        return True  # All moves are valid

    def ensure_valid_move(
        self, player: 'PlayerAgent')-> None:
        valid_move = False
        while not valid_move:
            if self.phase == 0:
                # Phase 0: Initial troop placement 
                # (single move treated as a list with one move)
                moves, reasoning, _  = (
                    player.make_initial_troop_placement(self.game_state))
            elif self.phase == 1:
                # Phase 1: Troop placement (multiple moves)
                moves, reasoning, _ = (
                    player.make_troop_placement(self.game_state))
            else:
                raise ValueError(f"Unknown phase: {self.phase}")

            #print(f"Proposed moves: {moves}, Reasoning: {reasoning}")
            if self.validate_move(player, moves, reasoning):
                print("Moves are valid")
                self.update_game_state_for_multiple_moves(player, moves)
                self.reduce_player_troops_for_multiple_moves(player, moves)
                valid_move = True
            else:
                print("Moves are invalid, asking for new moves")

    def ensure_valid_fortify_move(
        self, player: 'PlayerAgent')-> None:
        fortify_tries = 0
        while fortify_tries < 3:
            moves, reasoning, from_territory = (
                player.make_fortify_move(self.game_state)
            ) 
            # print(f"Proposed moves: {moves}, Reasoning: {reasoning}")
            if self.validate_fortify_move(
                player, moves,reasoning, from_territory):
                print("Moves are valid")
                self.update_game_state_for_fortify_move(
                    player, moves, from_territory)
                fortify_tries = 4  # Exit the loop
            else:
                print("Moves are invalid, asking for new moves")
                fortify_tries += 1
    
    def validate_fortify_move(
        self, player: 'PlayerAgent', 
        moves: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> bool:
       
        territory = moves[0].get('territory_name')
        num_troops = moves[0].get('num_troops')

        if territory is None or num_troops is None:
            print("Error: Territory or num_troops is None")
            return False
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not fortify")
            return True  # Blank move is valid

        if not self.game_state.check_terr_control(
            player.name, territory):
            print(f'''Error: {player.name} does not control to 
                    territory {territory}''')
            return False
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            print(f"Error: {player.name} does not control from " +
                f"territory {territory}")
            return False
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            print(f"Error: Not enough troops to fortify. {player.name} has " +
            f"only {from_territory_troops} troop(s) in {from_territory} but " +
            f"trying to move {num_troops}.")
            return False
        
        # Check if the territories are connected
        if not self.game_state.are_territories_connected(
            player.name, from_territory, territory):
            print(f"Error: Territories are not connected")
            return False

        # Optionally handle reasoning here
        if reasoning:
            print(f"Reasoning: {reasoning}")

        return True  # All moves are valid
    
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
        while invalid_attacks < 3:
            move, reasoning, from_territory = (
                player.make_attack_move(self.game_state, successful_attacks)
            ) 
            print(f"Proposed attack: {move} from {from_territory}, " +
                  f"Reasoning: {reasoning}")
            if self.validate_attack_move(
                player, move, reasoning, from_territory):
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
                print("Moves are invalid, asking for new moves")
                invalid_attacks += 1
        return successful_attacks

    def validate_attack_move(
        self, player: 'PlayerAgent', 
        move: List[Dict[str, int]], 
        reasoning: Optional[str] = None,
        from_territory: Optional[str] = None
    ) -> bool:
        total_troops = 0
       
        territory = move[0].get('territory_name')
        num_troops = move[0].get('num_troops')
        
        #print(f'''Validating move: Territory: {territory}, 
        #        Num troops: {num_troops}''')

        if territory is None or num_troops is None:
            print("Error: Territory or num_troops is None")
            return False
        
        if territory == 'Blank' or num_troops == 0:
            print("Choosing to not attack!!")
            return True  # Blank move is valid

        if self.game_state.check_terr_control(
            player.name, territory):
            print(f"Error: {player.name} already controls " +
                  f"territory {territory}")
            return False
            
        if not self.game_state.check_terr_control(
            player.name, from_territory):
            print(f"Error: {player.name} does not control from " +
                f"territory {territory}")
            return False
        
        from_territory_troops = self.game_state.check_number_of_troops(
            player.name, from_territory) 

        if num_troops >= from_territory_troops:
            print(f"Error: Not enough troops to Attack. {player.name} has " +
            f"only {from_territory_troops} troop(s) in {from_territory} but " +
            f"trying to attack with {num_troops}.")
            return False
        
        # Check if the territories are adjacent
        if not self.game_state.check_if_adjacent(from_territory, territory):
            print(f"Error: Territories are not connected")
            return False

        # Optionally handle reasoning here
        if reasoning:
            print(f"Reasoning: {reasoning}")

        return True  # All moves are valid
