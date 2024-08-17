import random
from typing import List, Dict
from risk_game.game_constants import STANDARD_CARD_DECK, TERRITORIES

class Card:
    def __init__(self, territory: str, troop_type: str) -> None:
        self.territory = territory
        self.troop_type = troop_type

    def __repr__(self):
        return f"Card(territory={self.territory}, troop_type={self.troop_type})"

class Deck:
    def __init__(self, card_list: List[Dict[str, str]] = STANDARD_CARD_DECK):
        self.cards = [Card(card["territory"], card["troop_type"]) for card in card_list]
        random.shuffle(self.cards)

    def draw_card(self, discarded_cards: List[Card]) -> Card:
        if not self.cards and discarded_cards:
            print("Reshuffling discard pile into deck")
            self.cards = discarded_cards[:]
            random.shuffle(self.cards)
            discarded_cards.clear()
        
        if self.cards:
            return self.cards.pop()
        else:
            return None
        

    def create_deck_of_random_cards(
        territories: List[str] = TERRITORIES
    ) -> List[Dict[str, str]]:
    
        # Shuffle the list of territories
        random.shuffle(territories)

        # Number of troop types
        troop_types = ["infantry", "cavalry", "canon"]

        # Split territories into three equal parts
        num_territories = len(territories)
        split_size = num_territories // 3

        # Create the list of cards
        cards = []

        # Add infantry, cavalry, and canon cards
        for i, territory in enumerate(territories):
            troop_type = troop_types[i // split_size % 3]
            cards.append({"territory": territory, "troop_type": troop_type})

        # Add 5 wild cards
        for _ in range(5):
            cards.append({"territory": "Wild Card", "troop_type": "wild"})

        # Shuffle the cards to randomize the order
        random.shuffle(cards)

        # Print the entire list of cards
        for card in cards:
            print(card)

        return cards