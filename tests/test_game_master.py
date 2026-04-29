import random
import unittest
from unittest.mock import patch

from risk_game.card_deck import Card
import pytest

from tests.helpers import get_player, make_game_master, set_territory_owner

pytestmark = pytest.mark.regression


class GameMasterTests(unittest.TestCase):
    def test_calculate_initial_troops_matches_expected_values(self):
        game_master = make_game_master("Alice", "Bob")

        self.assertEqual(game_master.calculate_initial_troops(2), 40)
        self.assertEqual(game_master.calculate_initial_troops(3), 35)
        self.assertEqual(game_master.calculate_initial_troops(4), 30)
        self.assertEqual(game_master.calculate_initial_troops(5), 25)
        self.assertEqual(game_master.calculate_initial_troops(6), 20)

    def test_validate_move_phase_0_rejects_unowned_territory(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        set_territory_owner(game_master.game_state, "Alaska", "Bob", 2)

        is_valid, error = game_master.validate_move_phase_0(
            alice, [{"territory_name": "Alaska", "num_troops": 1}]
        )

        self.assertFalse(is_valid)
        self.assertIn("does not control territory Alaska", error)
        self.assertEqual(alice.troop_placement_errors, 1)

    def test_validate_move_phase_1_requires_all_troops_to_be_placed(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        alice.troops = 3
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 2)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 1)

        is_valid, error = game_master.validate_move_phase_1(
            alice,
            [
                {"territory_name": "Alaska", "num_troops": 1},
                {"territory_name": "Alberta", "num_troops": 1},
            ],
        )

        self.assertFalse(is_valid)
        self.assertIn("Not placing all troops", error)

    def test_complete_initial_troop_placement_alternates_single_troop_moves(self):
        game_master = make_game_master("Alice", "Bob")
        game_master.distribute_territories_random()
        alice = get_player(game_master.active_players, "Alice")
        bob = get_player(game_master.active_players, "Bob")
        alice_target = game_master.game_state.get_player_territories("Alice")[0]
        bob_target = game_master.game_state.get_player_territories("Bob")[0]
        alice_start = game_master.game_state.get_sum_of_player_troops("Alice")
        bob_start = game_master.game_state.get_sum_of_player_troops("Bob")
        alice.troops = 2
        bob.troops = 2
        game_master.current_player_index = 0
        call_order = []

        def alice_move(*args, **kwargs):
            call_order.append("Alice")
            return (
                [{"territory_name": alice_target, "num_troops": 1}],
                "Reinforce Alice frontier.",
                None,
            )

        def bob_move(*args, **kwargs):
            call_order.append("Bob")
            return (
                [{"territory_name": bob_target, "num_troops": 1}],
                "Reinforce Bob frontier.",
                None,
            )

        with patch.object(
            alice,
            "make_initial_troop_placement",
            side_effect=alice_move,
        ), patch.object(
            bob,
            "make_initial_troop_placement",
            side_effect=bob_move,
        ), patch.object(
            game_master,
            "calculate_initial_troops",
            return_value=alice_start + 2,
        ):
            game_master.complete_initial_troop_placement()

        self.assertEqual(alice.troops, 0)
        self.assertEqual(bob.troops, 0)
        self.assertEqual(
            game_master.game_state.get_sum_of_player_troops("Alice"),
            alice_start + 2,
        )
        self.assertEqual(
            game_master.game_state.get_sum_of_player_troops("Bob"),
            bob_start + 2,
        )
        first_player = game_master.active_players[0].name
        second_player = game_master.active_players[1].name
        self.assertEqual(
            call_order,
            [first_player, second_player, first_player, second_player],
        )

    def test_validate_attack_move_rejects_non_adjacent_target(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 4)
        set_territory_owner(game_master.game_state, "Peru", "Bob", 2)

        is_valid, error = game_master.validate_attack_move(
            alice,
            [{"territory_name": "Peru", "num_troops": 2}],
            from_territory="Alberta",
        )

        self.assertFalse(is_valid)
        self.assertEqual(error, "Error: Territories are not connected")

    def test_validate_fortify_move_accepts_connected_owned_chain(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 4)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 2)
        set_territory_owner(game_master.game_state, "Western United States", "Alice", 1)

        is_valid, error = game_master.validate_fortify_move(
            alice,
            [{"territory_name": "Western United States", "num_troops": 2}],
            from_territory="Alaska",
        )

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_generate_random_troop_placement_initial_placement_uses_single_troop(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        alice.troops = 5
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 3)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 2)

        random.seed(7)
        moves = game_master.generate_random_troop_placement(
            alice, game_master.game_state, initial_placement=True
        )

        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["num_troops"], 1)
        self.assertIn(moves[0]["territory_name"], {"Alaska", "Alberta"})

    def test_generate_random_troop_placement_uses_all_available_troops(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        alice.troops = 6
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 3)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 2)
        set_territory_owner(game_master.game_state, "Ontario", "Alice", 1)

        random.seed(3)
        moves = game_master.generate_random_troop_placement(
            alice, game_master.game_state, initial_placement=False
        )

        self.assertEqual(sum(move["num_troops"] for move in moves), 6)
        self.assertTrue(all(move["territory_name"] in {"Alaska", "Alberta", "Ontario"} for move in moves))

    def test_update_game_state_for_fortify_move_moves_troops_between_owned_territories(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 2)

        game_master.update_game_state_for_fortify_move(
            alice,
            [{"territory_name": "Alberta", "num_troops": 3}],
            "Alaska",
        )

        self.assertEqual(game_master.game_state.check_number_of_troops("Alice", "Alaska"), 2)
        self.assertEqual(game_master.game_state.check_number_of_troops("Alice", "Alberta"), 5)

    def test_remove_player_moves_them_to_dead_players(self):
        game_master = make_game_master("Alice", "Bob", "Cara")
        game_master.current_player_index = 1

        game_master.remove_player("Alice")

        self.assertEqual([player.name for player in game_master.dead_players], ["Alice"])
        self.assertEqual(sorted(player.name for player in game_master.active_players), ["Bob", "Cara"])
        self.assertEqual(game_master.game_state.num_players, 2)

    def test_ask_to_trade_in_cards_uses_full_selected_combination(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        set_territory_owner(game_master.game_state, "Brazil", "Alice", 2)

        game_master.player_cards[alice.name] = [
            Card("Brazil", "infantry"),
            Card("Peru", "cavalry"),
            Card("North Africa", "canon"),
        ]

        with patch.object(
            alice,
            "may_trade_cards",
            return_value=([1, 2, 3], "Trade the matching set."),
        ):
            game_master.ask_to_trade_in_cards(alice)

        self.assertEqual(len(game_master.player_cards[alice.name]), 0)
        self.assertEqual(len(game_master.discarded_cards), 3)
        self.assertEqual(alice.card_trade_errors, 0)
        self.assertEqual(game_master.rules.trade_count, 1)

    def test_phase_2_attack_does_not_award_card_when_player_skips_immediately(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")

        with patch.object(
            alice,
            "make_attack_move",
            return_value=(
                [{"territory_name": "Blank", "num_troops": 0}],
                "Stop attacking.",
                "Blank",
            ),
        ), patch.object(
            game_master.deck,
            "draw_card",
            side_effect=AssertionError("draw_card should not be called"),
        ):
            game_master.phase_2_attack(alice)

        self.assertEqual(game_master.player_cards[alice.name], [])

    def test_phase_2_attack_awards_card_after_success_then_stop(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        bob = get_player(game_master.active_players, "Bob")

        attack_sequence = [
            (
                [{"territory_name": "Brazil", "num_troops": 3}],
                "Take Brazil.",
                "Argentina",
            ),
            (
                [{"territory_name": "Blank", "num_troops": 0}],
                "Stop attacking.",
                "Blank",
            ),
        ]

        with patch.object(
            alice,
            "make_attack_move",
            side_effect=attack_sequence,
        ), patch.object(
            game_master,
            "validate_attack_move",
            side_effect=[(True, None), (True, None)],
        ), patch.object(
            game_master.game_state,
            "update_game_state_for_attack_move",
            side_effect=[("win", bob.name), ("no_attack", "_")],
        ), patch.object(
            game_master,
            "is_game_over",
            return_value=False,
        ), patch.object(
            game_master.deck,
            "draw_card",
            return_value=Card("Peru", "cavalry"),
        ) as draw_card:
            game_master.phase_2_attack(alice)

        draw_card.assert_called_once()
        self.assertEqual(len(game_master.player_cards[alice.name]), 1)
        self.assertEqual(game_master.player_cards[alice.name][0].territory, "Peru")

    def test_play_a_turn_skips_attack_and_fortify_after_turn_timeout(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")

        def expire_turn(player):
            player.turn_time_exhausted = True

        with patch.object(game_master, "_start_turn_trace"), patch.object(
            game_master,
            "_finalize_turn_trace",
            return_value={"turn_number": 1},
        ), patch.object(
            game_master,
            "phase_1_troop_placement",
            side_effect=expire_turn,
        ), patch.object(
            game_master,
            "phase_2_attack",
        ) as attack_phase, patch.object(
            game_master,
            "phase_3_fortify",
        ) as fortify_phase:
            game_master.play_a_turn(alice, turn_number=1)

        attack_phase.assert_not_called()
        fortify_phase.assert_not_called()


if __name__ == "__main__":
    unittest.main()
