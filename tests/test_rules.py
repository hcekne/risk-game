import unittest
import pytest

from risk_game.card_deck import Card
from risk_game.game_constants import TERRITORIES
from tests.helpers import get_player, make_game_state, set_territory_owner

pytestmark = pytest.mark.regression


class RulesTests(unittest.TestCase):
    def test_verify_card_combination_adds_bonus_for_owned_card_territory(self):
        _, game_state, rules = make_game_state("Alice", "Bob", progressive=False)
        set_territory_owner(game_state, "Brazil", "Alice", 2)
        cards = [
            Card("Brazil", "infantry"),
            Card("Peru", "cavalry"),
            Card("North Africa", "canon"),
        ]

        is_valid, troops, wildcard_used = rules.verify_card_combination(
            cards, "Alice", game_state
        )

        self.assertTrue(is_valid)
        self.assertEqual(troops, 11)
        self.assertFalse(wildcard_used)

    def test_calculate_troops_includes_continent_and_capital_bonus(self):
        _, game_state, rules = make_game_state("Alice", "Bob", capitals=True)
        for territory in ["Venezuela", "Peru", "Brazil", "Argentina"]:
            set_territory_owner(game_state, territory, "Alice", 1)
        game_state.set_capital("Alice", "Brazil")

        total_troops = rules.calculate_troops(
            game_state.get_player_territories("Alice"), game_state
        )

        self.assertEqual(total_troops, 7)

    def test_check_territory_control_percentage_uses_total_board_size(self):
        players, game_state, rules = make_game_state(
            "Alice", "Bob", territory_control_percentage=0.6, max_rounds=20
        )

        for territory in TERRITORIES[:26]:
            set_territory_owner(game_state, territory, "Alice", 1)
        for territory in TERRITORIES[26:]:
            set_territory_owner(game_state, territory, "Bob", 1)

        self.assertTrue(rules.check_territory_control_percentage(game_state, players[0]))
        self.assertFalse(rules.check_territory_control_percentage(game_state, players[1]))

    def test_check_victory_conditions_uses_territory_leader_at_max_rounds(self):
        players, game_state, rules = make_game_state(
            "Alice",
            "Bob",
            territory_control_percentage=1.0,
            max_rounds=5,
        )
        alice = get_player(players, "Alice")
        bob = get_player(players, "Bob")

        for territory in TERRITORIES[:25]:
            set_territory_owner(game_state, territory, "Alice", 1)
        for territory in TERRITORIES[25:]:
            set_territory_owner(game_state, territory, "Bob", 1)

        game_over, winner_name, victory_condition = rules.check_victory_conditions(
            game_state, alice, current_round=5, active_players=[alice, bob]
        )

        self.assertTrue(game_over)
        self.assertEqual(winner_name, "Alice")
        self.assertEqual(victory_condition, "Max Rounds Reached - Territory Control")

    def test_check_capital_control_requires_all_capitals(self):
        players, game_state, rules = make_game_state("Alice", "Bob", capitals=True)
        alice = get_player(players, "Alice")

        set_territory_owner(game_state, "Brazil", "Alice", 3)
        set_territory_owner(game_state, "Alaska", "Alice", 2)
        game_state.set_capital("Alice", "Brazil")
        game_state.set_capital("Bob", "Alaska")

        self.assertTrue(rules.check_capital_control(game_state, alice))

        set_territory_owner(game_state, "Alaska", "Bob", 2)
        self.assertFalse(rules.check_capital_control(game_state, alice))

    def test_find_valid_combinations_returns_tradeable_sets_grouped_by_value(self):
        _, game_state, rules = make_game_state("Alice", "Bob", progressive=False)
        cards = [
            Card("Brazil", "infantry"),
            Card("Peru", "cavalry"),
            Card("North Africa", "canon"),
            Card("Argentina", "infantry"),
        ]

        valid_combinations = rules.find_valid_combinations(cards, "Alice", game_state)

        self.assertIn(10, valid_combinations)
        self.assertIn(([1, 2, 3], False), valid_combinations[10])


if __name__ == "__main__":
    unittest.main()
