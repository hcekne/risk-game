import unittest

import pytest

from risk_game.card_deck import Card
from risk_game.player_agent import PlayerAgent
from tests.helpers import (
    RecordingLLMClient,
    make_game_state,
    seed_full_board,
    set_territory_owner,
)


pytestmark = pytest.mark.regression


class StateRepresentationTests(unittest.TestCase):
    def test_compact_player_view_is_shorter_than_verbose_view(self):
        _, game_state, _ = make_game_state("Alice", "Bob", "Cara")
        seed_full_board(game_state, ["Alice", "Bob", "Cara"])
        set_territory_owner(game_state, "Ontario", "Alice", 5)
        set_territory_owner(game_state, "Brazil", "Alice", 4)
        set_territory_owner(game_state, "Ukraine", "Bob", 6)

        verbose_view = game_state.format_game_state()
        compact_view = game_state.format_game_state_for_player("Alice")

        self.assertLess(len(compact_view), len(verbose_view))
        self.assertIn("Player key:", compact_view)
        self.assertIn("Standings:", compact_view)
        self.assertIn("Your borders:", compact_view)
        self.assertIn("World map by continent", compact_view)

    def test_attack_and_fortify_views_include_concrete_legal_options(self):
        _, game_state, _ = make_game_state("Alice", "Bob")
        for territory in game_state.territories_df["Territory"]:
            set_territory_owner(game_state, territory, "Bob", 1)

        set_territory_owner(game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_state, "Alberta", "Alice", 3)
        set_territory_owner(game_state, "Ontario", "Alice", 2)
        set_territory_owner(game_state, "Western United States", "Alice", 1)
        set_territory_owner(game_state, "Northwest Territory", "Bob", 2)
        set_territory_owner(game_state, "Kamchatka", "Bob", 2)
        set_territory_owner(game_state, "Greenland", "Bob", 1)
        set_territory_owner(game_state, "Eastern United States", "Bob", 1)
        set_territory_owner(game_state, "Central America", "Bob", 1)

        attack_vectors = game_state.get_adjacent_enemy_territories(
            "Alice", game_state.get_strong_territories_with_troops("Alice")
        )
        attack_text = game_state.format_adjacent_enemy_territories(
            attack_vectors, player_name="Alice"
        )
        fortify_text = game_state.format_fortify_options("Alice")

        self.assertIn("Alaska max=4", attack_text)
        self.assertIn("Northwest Territory P2(2)", attack_text)
        self.assertIn("Kamchatka P2(2)", attack_text)
        self.assertIn("From Ontario max=1", fortify_text)
        self.assertIn("Alaska(5, enemy_neighbors=2)", fortify_text)

    def test_player_agent_prompts_use_compact_state_view(self):
        client = RecordingLLMClient(
            response=(
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Hold position+++"
            )
        )
        player = PlayerAgent("Alice", client)
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_state, "Alberta", "Alice", 3)
        set_territory_owner(game_state, "Ontario", "Bob", 2)
        player.turn_strategy = "Hold borders."

        player.define_strategy_for_move(rules, game_state)
        self.assertIn("Game snapshot:", client.last_message)
        self.assertIn("Attack options:", client.last_message)
        self.assertNotIn("Controlled by", client.last_message)

        player.make_attack_move(rules, game_state, successful_attacks=0)
        self.assertIn("Game snapshot:", client.last_message)
        self.assertIn("Player key:", client.last_message)
        self.assertIn("Attack options:", client.last_message)

    def test_attack_and_fortify_prompts_preserve_output_grammar(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_state, "Alberta", "Alice", 3)
        set_territory_owner(game_state, "Ontario", "Bob", 2)

        attack_client = RecordingLLMClient(
            response=(
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Pause+++"
            )
        )
        attack_player = PlayerAgent("Alice", attack_client)
        attack_player.turn_strategy = "Reinforce Alaska and pressure Ontario."
        attack_player.make_attack_move(rules, game_state, successful_attacks=1)

        self.assertIn("LEGAL OPTIONS:", attack_client.last_message)
        self.assertIn("TURN PLAN:", attack_client.last_message)
        self.assertLess(
            attack_client.last_message.index("LEGAL OPTIONS:"),
            attack_client.last_message.index("TURN PLAN:"),
        )
        self.assertIn(
            "Attack Opponent Territory:||| Territory, Number of troops|||",
            attack_client.last_message,
        )
        self.assertIn("From Territory: ### From Territory ###", attack_client.last_message)
        self.assertIn("Attack Opponent Territory:|||Blank, 0|||", attack_client.last_message)

        fortify_client = RecordingLLMClient(
            response=(
                "To Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Hold+++"
            )
        )
        fortify_player = PlayerAgent("Alice", fortify_client)
        fortify_player.turn_strategy = "Shift reserves toward the main border."
        fortify_player.make_fortify_move(rules, game_state)

        self.assertIn("LEGAL OPTIONS:", fortify_client.last_message)
        self.assertIn("TURN PLAN:", fortify_client.last_message)
        self.assertLess(
            fortify_client.last_message.index("LEGAL OPTIONS:"),
            fortify_client.last_message.index("TURN PLAN:"),
        )
        self.assertIn(
            "To Territory:|||To Territory, Number of troops|||",
            fortify_client.last_message,
        )
        self.assertIn("From Territory: ### From Territory ###", fortify_client.last_message)
        self.assertIn("To Territory:|||Blank, 0|||", fortify_client.last_message)

    def test_placement_trade_and_strategy_prompts_use_clear_stable_sections(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alaska", "Alice", 4)
        set_territory_owner(game_state, "Alberta", "Alice", 3)
        set_territory_owner(game_state, "Ontario", "Bob", 2)

        initial_client = RecordingLLMClient(
            response="Move:|||Alaska, 1|||\nReasoning:+++Border pressure+++"
        )
        initial_player = PlayerAgent("Alice", initial_client)
        initial_player.placement_time_limit_seconds = None
        initial_player.make_initial_troop_placement(rules, game_state)
        self.assertIn("PACE:", initial_client.last_message)
        self.assertIn("Placement snapshot:", initial_client.last_message)
        self.assertIn("LEGAL PLACEMENT TARGETS:", initial_client.last_message)
        self.assertIn("Move:|||Territory, Number of troops|||", initial_client.last_message)
        self.assertIn("RESPONSE RULES:", initial_client.last_message)

        placement_client = RecordingLLMClient(
            response="Move 1: |||Alaska, 3|||\nReasoning:+++Stack one front+++"
        )
        placement_player = PlayerAgent("Alice", placement_client)
        placement_player.placement_time_limit_seconds = None
        placement_player.troops = 3
        placement_player.make_troop_placement(rules, game_state)
        self.assertIn("PACE:", placement_client.last_message)
        self.assertIn("Placement snapshot:", placement_client.last_message)
        self.assertIn("LEGAL PLACEMENT TARGETS:", placement_client.last_message)
        self.assertIn("Move 1: |||Territory, Number of troops|||", placement_client.last_message)
        self.assertIn("The total troops placed across all moves must equal 3.", placement_client.last_message)

        strategy_client = RecordingLLMClient(response="- Reinforce Alaska.\n- Skip bad attacks.")
        strategy_player = PlayerAgent("Alice", strategy_client)
        strategy_player.define_strategy_for_move(rules, game_state)
        self.assertIn("Two short bullet points maximum.", strategy_client.last_message)
        self.assertIn("Maximum 60 words total.", strategy_client.last_message)
        self.assertIn("LEGAL ATTACK OVERVIEW:", strategy_client.last_message)

        cards = [
            Card("Brazil", "infantry"),
            Card("Peru", "cavalry"),
            Card("North Africa", "canon"),
        ]
        valid_combinations = {4: [([1, 2, 3], False)]}

        must_trade_client = RecordingLLMClient(
            response="List of cards to trade ||| 1, 2, 3 |||"
        )
        must_trade_player = PlayerAgent("Alice", must_trade_client)
        must_trade_player.must_trade_cards(cards, game_state, valid_combinations)
        self.assertIn("VALID COMBINATIONS:", must_trade_client.last_message)
        self.assertIn(
            "List of cards to trade ||| [Card Numbers] |||",
            must_trade_client.last_message,
        )

        may_trade_client = RecordingLLMClient(response="||| 0 |||")
        may_trade_player = PlayerAgent("Alice", may_trade_client)
        may_trade_player.may_trade_cards(cards, game_state, valid_combinations)
        self.assertIn("CURRENT STATE:", may_trade_client.last_message)
        self.assertIn("VALID COMBINATIONS:", may_trade_client.last_message)
        self.assertIn("||| 0 |||", may_trade_client.last_message)
