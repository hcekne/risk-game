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
        self.rules = Rules()
        self.current_player_index = -1
        self.deck = None
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
            print(f"Player {player_name} not found in active players")

    def list_players(self) -> None:
        for player in self.players:
            print(f"Name: {player.name}")

    def validate_move(
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
                
    def update_game_state(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
    ) -> None:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        self.game_state.update_troops(player, territory, num_troops)

    def reduce_player_troops(
        self, player: 'PlayerAgent', 
        move: Tuple[Optional[str], Optional[int], Optional[str]]
    ) -> None:
        territory, num_troops, _ = move  # Unpack the tuple, ignore reasoning
        player.troops -= num_troops

    def ensure_valid_move(self, player: 'PlayerAgent'):
        valid_move = False
        while not valid_move:
            move = player.make_initial_troop_placement(self.game_state)
            print(f"Proposed move: {move}")
            if self.validate_move(player, move):
                print("Move is valid")
                self.update_game_state(player, move)
                self.reduce_player_troops(player, move)
                valid_move = True
            else:
                print("Move is invalid, asking for a new move")

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
        print(f"Player {player.name} is starting their turn.")
        # Phase 1: Troop Placement
        self.phase_1_troop_placement(player)
        self.phase_2_attack(player)
        self.phase_3_fortify(player)
        print(f"Player {player.name} has completed their turn.")
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
            player.troops_left += troops
            print(f"{player.name} traded in cards for {troops} extra troops.")
        else:
            print(f"Invalid trade attempt by {player.name}.")

    def phase_1_troop_placement(self, player: 'PlayerAgent')-> None:
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


        # get the territories the player controls
        # pass the player and the territories and the number of troops to the player agent
        # get the move from the player agent
        # validate the move
        # update the game state
        # reduce the number of troops for the player
        # end phase 1
        pass

    def phase_2_attack(self, player: 'PlayerAgent')-> None:
        print(f"Player {player.name} is attacking")

        # if player conquered a territory in phase 2, they get a card
        # need to check for this



        # 1. pass the player the game state and ask if he wants to attack 
        # another territory
        # 2.
        pass

    def phase_3_fortify(self, player: 'PlayerAgent') -> None:
        print(f"Player {player.name} is fortifying")
        # end phase 3
        pass

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
            self.game_round += 1
            # remove any players with no territories
            # first create a list of players to remove
            # iteratate through list and remove players

            
            print(f'Starting round: {self.game_round}')
            for player in self.active_players:
                self.play_a_turn(player)
                # check if the game is over
                if self.is_game_over():
                    break


        print("Game over")
        print(f"Player {self.game_state.get_winner()} wins")
        print(f"Game lasted {self.game_round} rounds")


