# rules.py
from typing import List, Tuple
from risk_game.card_deck import Card
from risk_game.game_utils import CONTINENT_BONUSES


class Rules:
    def __init__(
            self, progressive: bool = False, 
            capitals: bool = False, mode: str = "world_domination"):
        self.progressive = progressive
        self.capitals = capitals
        self.mode = mode
        self.trade_count = 0  # Track the number of trades for progressive mode

    def verify_card_combination(self, cards: List[Card]) -> Tuple[bool, int]:
        if len(cards) != 3:
            return False, 0  # Invalid number of cards

        # Count the number of each type of card
        infantry_nr = sum(1 for card in cards if card.troop_type == "infantry")
        cavalry_nr = sum(1 for card in cards if card.troop_type == "cavalry")
        artillery_nr = sum(1 for card in cards if card.troop_type == "canon")
        wildcard_nr = sum(1 for card in cards if card.troop_type == "wild")

        # One of each type (Infantry, Cavalry, Artillery) - consider wildcards
        if (infantry_nr >= 1 and cavalry_nr >= 1 and artillery_nr >= 1) or \
           (infantry_nr >= 1 and cavalry_nr >= 1 and wildcard_nr >= 1) or \
           (infantry_nr >= 1 and artillery_nr >= 1 and wildcard_nr >= 1) or \
           (cavalry_nr >= 1 and artillery_nr >= 1 and wildcard_nr >= 1) or \
           (infantry_nr == 1 and cavalry_nr == 1 and artillery_nr == 1):
            return (True, 
                self.calculate_progressive_troops() if self.progressive else 10)

        # Three of a kind (Infantry, Cavalry, or Artillery) - consider wildcards
        if artillery_nr + wildcard_nr == 3:
            return (True, 
                self.calculate_progressive_troops() if self.progressive else 8)
        if cavalry_nr + wildcard_nr == 3:
            return (True, 
                self.calculate_progressive_troops() if self.progressive else 6)
        if infantry_nr + wildcard_nr == 3:
            return (True, 
                self.calculate_progressive_troops() if self.progressive else 4)

        # If none of the above, the combination is invalid
        return False, 0
    
    def has_valid_combination(self, cards: List[Card]) -> Tuple[bool]:
        if len(cards) < 3:
            return False  # Not enough cards to trade

        # Count the number of each type of card
        infantry_nr = sum(1 for card in cards if card.troop_type == "infantry")
        cavalry_nr = sum(1 for card in cards if card.troop_type == "cavalry")
        artillery_nr = sum(1 for card in cards if card.troop_type == "canon")
        wildcard_nr = sum(1 for card in cards if card.troop_type == "wild")

        # One of each type (Infantry, Cavalry, Artillery) - considering wildcards
        if (infantry_nr >= 1 and cavalry_nr >= 1 and artillery_nr >= 1) or \
           (infantry_nr >= 1 and cavalry_nr >= 1 and wildcard_nr >= 1) or \
           (infantry_nr >= 1 and artillery_nr >= 1 and wildcard_nr >= 1) or \
           (cavalry_nr >= 1 and artillery_nr >= 1 and wildcard_nr >= 1) or \
           (infantry_nr == 1 and cavalry_nr == 1 and artillery_nr == 1):
            return True

        # Three of a kind (Infantry, Cavalry, or Artillery) - considering wildcards
        if artillery_nr + wildcard_nr == 3:
            return True
        if cavalry_nr + wildcard_nr == 3:
            return True
        if infantry_nr + wildcard_nr == 3:
            return True, 
        # If none of the above, the combination is invalid
        return False

    
    def calculate_progressive_troops(self) -> int:
        # Progressive troop schedule based on the trade count
        if self.trade_count == 0:
            troops = 4
        elif self.trade_count == 1:
            troops = 6
        elif self.trade_count == 2:
            troops = 8
        elif self.trade_count == 3:
            troops = 10
        elif self.trade_count == 4:
            troops = 12
        elif self.trade_count == 5:
            troops = 15
        elif self.trade_count >= 6:
            troops = self.trade_count*5 - 10  # Increase by 5 troops after 6.

        self.trade_count += 1  # Increment trade count after each trade
        return troops

    def reset_trade_count(self):
        self.trade_count = 0

    
    def calculate_troops(self, player_territories: List[str], game_state) -> int:
        # Calculate the base troops (1 troop per 3 territories, with a min of 3)
        base_troops = max(len(player_territories) // 3, 3)
        
        # Calculate continent bonuses
        continent_bonus = self.calculate_continent_bonus(player_territories)
        
        # Calculate any additional bonuses if applicable (e.g., for capitals)
        additional_bonus = (
            self.calculate_additional_bonuses(player_territories, game_state))
        
        # Total troops
        total_troops = base_troops + continent_bonus + additional_bonus
        
        return total_troops
    
    def calculate_continent_bonus(self, player_territories: List[str]) -> int:
        continent_bonus = 0
        for continent, (territories, bonus) in CONTINENT_BONUSES.items():
            if all(territory in player_territories for territory in territories):
                continent_bonus += bonus
        return continent_bonus  

    def calculate_additional_bonuses(
        self, player_territories: List[str], game_state) -> int:
        additional_bonus = 0
        if self.capitals:
            for territory in player_territories:
                if game_state.is_capital(territory):
                    additional_bonus += 2
        return additional_bonus     


