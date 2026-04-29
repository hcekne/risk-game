import unittest
from unittest.mock import patch
import pytest

from tests.helpers import get_player, make_game_state, set_territory_owner

pytestmark = pytest.mark.regression


class GameStateTests(unittest.TestCase):
    def test_assign_territories_randomly_covers_all_territories_once(self):
        players, game_state, _ = make_game_state("Alice", "Bob", "Cara")
        for player in players:
            player.troops = 30

        last_player_index = game_state.assign_territories_to_players_random(players)

        owner_counts = game_state.territories_df.iloc[:, 1:].gt(0).sum(axis=1)

        self.assertTrue(game_state.validate_territory_assignment())
        self.assertTrue((owner_counts == 1).all())
        self.assertEqual(last_player_index, 2)
        for player in players:
            self.assertEqual(player.troops, 16)

    def test_are_territories_connected_requires_owned_path(self):
        _, game_state, _ = make_game_state("Alice", "Bob")
        set_territory_owner(game_state, "Alaska", "Alice", 3)
        set_territory_owner(game_state, "Alberta", "Alice", 2)
        set_territory_owner(game_state, "Western United States", "Alice", 1)
        set_territory_owner(game_state, "Ontario", "Bob", 4)

        self.assertTrue(
            game_state.are_territories_connected(
                "Alice", "Alaska", "Western United States"
            )
        )
        self.assertFalse(game_state.are_territories_connected("Alice", "Alaska", "Ontario"))

    def test_get_adjacent_enemy_territories_excludes_owned_neighbors(self):
        _, game_state, _ = make_game_state("Alice", "Bob")
        set_territory_owner(game_state, "Brazil", "Alice", 4)
        set_territory_owner(game_state, "Peru", "Alice", 2)
        set_territory_owner(game_state, "Venezuela", "Bob", 1)
        set_territory_owner(game_state, "Argentina", "Bob", 3)
        set_territory_owner(game_state, "North Africa", "Bob", 5)

        result = game_state.get_adjacent_enemy_territories("Alice", [("Brazil", 3)])

        self.assertEqual(result["Brazil"][0], 3)
        self.assertEqual(result["Brazil"][1], ["Venezuela", "Argentina", "North Africa"])

    def test_attack_win_transfers_control_to_attacker(self):
        players, game_state, _ = make_game_state("Alice", "Bob")
        alice = get_player(players, "Alice")
        set_territory_owner(game_state, "Alberta", "Alice", 5)
        set_territory_owner(game_state, "Alaska", "Bob", 3)

        with patch.object(game_state, "simulate_attack", return_value=("attacker", 2)):
            outcome, defender = game_state.update_game_state_for_attack_move(
                alice, [{"territory_name": "Alaska", "num_troops": 3}], "Alberta"
            )

        self.assertEqual((outcome, defender), ("win", "Bob"))
        self.assertEqual(game_state.check_number_of_troops("Alice", "Alberta"), 2)
        self.assertEqual(game_state.check_number_of_troops("Alice", "Alaska"), 2)
        self.assertEqual(game_state.check_number_of_troops("Bob", "Alaska"), 0)

    def test_attack_loss_keeps_defender_in_control(self):
        players, game_state, _ = make_game_state("Alice", "Bob")
        alice = get_player(players, "Alice")
        set_territory_owner(game_state, "Alberta", "Alice", 5)
        set_territory_owner(game_state, "Alaska", "Bob", 3)

        with patch.object(game_state, "simulate_attack", return_value=("defender", 1)):
            outcome, defender = game_state.update_game_state_for_attack_move(
                alice, [{"territory_name": "Alaska", "num_troops": 3}], "Alberta"
            )

        self.assertEqual((outcome, defender), ("lose", "Bob"))
        self.assertEqual(game_state.check_number_of_troops("Alice", "Alberta"), 2)
        self.assertEqual(game_state.check_number_of_troops("Alice", "Alaska"), 0)
        self.assertEqual(game_state.check_number_of_troops("Bob", "Alaska"), 1)

    def test_blank_attack_is_a_valid_no_op(self):
        players, game_state, _ = make_game_state("Alice", "Bob")
        alice = get_player(players, "Alice")
        set_territory_owner(game_state, "Alberta", "Alice", 5)
        set_territory_owner(game_state, "Alaska", "Bob", 3)

        outcome, defender = game_state.update_game_state_for_attack_move(
            alice, [{"territory_name": "Blank", "num_troops": 0}], "Alberta"
        )

        self.assertEqual((outcome, defender), ("no_attack", "_"))
        self.assertEqual(game_state.check_number_of_troops("Alice", "Alberta"), 5)
        self.assertEqual(game_state.check_number_of_troops("Bob", "Alaska"), 3)


if __name__ == "__main__":
    unittest.main()
