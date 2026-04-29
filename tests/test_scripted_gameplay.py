import random
import tempfile
import unittest
from unittest.mock import patch

import pytest

from tests.helpers import (
    assert_valid_board_state,
    make_scripted_game_master,
    owner_signature,
)


pytestmark = pytest.mark.regression


class ScriptedGameplayTests(unittest.TestCase):
    def test_scripted_agents_complete_multiple_turns_with_valid_transitions(self):
        random.seed(11)
        game = make_scripted_game_master(
            "Alpha",
            "Bravo",
            "Charlie",
            territory_control_percentage=0.65,
            max_rounds=8,
        )

        game.init_game_state()
        game.distribute_territories_random()
        game.complete_initial_troop_placement()

        assert_valid_board_state(self, game.game_state)

        ownership_changed = False
        previous_signature = owner_signature(game.game_state)

        for _ in range(3):
            game.game_round += 1
            for player in list(game.active_players):
                if player not in game.active_players:
                    continue
                if game.is_game_over():
                    break

                game.play_a_turn(player)
                assert_valid_board_state(self, game.game_state)

                current_signature = owner_signature(game.game_state)
                ownership_changed |= current_signature != previous_signature
                previous_signature = current_signature

            if game.is_game_over():
                break

        self.assertTrue(ownership_changed)
        for player in game.players:
            self.assertEqual(player.troop_placement_errors, 0)
            self.assertEqual(player.return_formatting_errors, 0)
            self.assertEqual(player.attack_errors, 0)
            self.assertEqual(player.fortify_errors, 0)
            self.assertEqual(player.card_trade_errors, 0)

    def test_scripted_agents_choose_owned_capitals(self):
        random.seed(7)
        game = make_scripted_game_master(
            "Alpha",
            "Bravo",
            "Charlie",
            capitals=True,
            territory_control_percentage=0.65,
            max_rounds=6,
        )

        game.init_game_state()
        game.distribute_territories_random()
        game.choose_capitals()

        self.assertEqual(len(game.game_state.capitals), len(game.active_players))
        for player in game.active_players:
            self.assertIsNotNone(player.capital)
            self.assertEqual(game.game_state.capitals[player.name], player.capital)
            self.assertTrue(game.game_state.check_terr_control(player.name, player.capital))

    def test_scripted_agents_finish_multiple_full_games_via_play_game(self):
        for seed in (3, 5, 9):
            random.seed(seed)
            game = make_scripted_game_master(
                "Alpha",
                "Bravo",
                "Charlie",
                territory_control_percentage=0.65,
                max_rounds=6,
            )

            saved_signatures = []

            def capture_game_state(game_state, game_folder, turn_number, game_round):
                assert_valid_board_state(self, game_state)
                saved_signatures.append(owner_signature(game_state))

            with tempfile.TemporaryDirectory() as temp_dir:
                with patch("risk_game.game_master.create_game_folder", return_value=temp_dir):
                    with patch("risk_game.game_master.save_game_state", side_effect=capture_game_state):
                        with patch("risk_game.game_master.save_player_data"):
                            with patch("risk_game.game_master.save_end_game_results"):
                                game.play_game(include_initial_troop_placement=True)

            self.assertTrue(game.game_over)
            self.assertIsNotNone(game.winner)
            self.assertGreater(len(saved_signatures), 4)
            self.assertTrue(
                any(
                    earlier != later
                    for earlier, later in zip(saved_signatures, saved_signatures[1:])
                )
            )
            for player in game.players:
                self.assertEqual(player.troop_placement_errors, 0)
                self.assertEqual(player.return_formatting_errors, 0)
                self.assertEqual(player.attack_errors, 0)
                self.assertEqual(player.fortify_errors, 0)
                self.assertEqual(player.card_trade_errors, 0)
