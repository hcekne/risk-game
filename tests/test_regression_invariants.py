import unittest
from unittest.mock import patch

import pytest

from tests.helpers import (
    assert_valid_board_state,
    get_player,
    make_game_master,
    make_game_state,
    seed_full_board,
    set_territory_owner,
)


pytestmark = pytest.mark.regression


class RegressionInvariantTests(unittest.TestCase):
    def test_random_territory_distribution_preserves_board_invariants(self):
        players, game_state, _ = make_game_state("Alice", "Bob", "Cara")
        for player in players:
            player.troops = 30

        game_state.assign_territories_to_players_random(players)

        assert_valid_board_state(self, game_state)

    def test_attack_resolution_preserves_board_invariants(self):
        players, game_state, _ = make_game_state("Alice", "Bob")
        alice = get_player(players, "Alice")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alberta", "Alice", 5)
        set_territory_owner(game_state, "Alaska", "Bob", 3)

        with patch.object(game_state, "simulate_attack", return_value=("attacker", 2)):
            game_state.update_game_state_for_attack_move(
                alice, [{"territory_name": "Alaska", "num_troops": 3}], "Alberta"
            )

        assert_valid_board_state(self, game_state)

    def test_fortify_update_preserves_board_invariants(self):
        game_master = make_game_master("Alice", "Bob")
        alice = get_player(game_master.active_players, "Alice")
        seed_full_board(game_master.game_state, ["Alice", "Bob"])
        set_territory_owner(game_master.game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_master.game_state, "Alberta", "Alice", 2)

        game_master.update_game_state_for_fortify_move(
            alice,
            [{"territory_name": "Alberta", "num_troops": 3}],
            "Alaska",
        )

        assert_valid_board_state(self, game_master.game_state)
