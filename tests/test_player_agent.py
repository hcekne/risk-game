import unittest
import json
import time
import tempfile
from pathlib import Path
from types import SimpleNamespace
import pytest

from risk_game.player_agent import PlayerAgent
from risk_game.utils.game_admin import build_llm_interaction_logger
from tests.helpers import (
    RecordingLLMClient,
    StubLLMClient,
    make_game_state,
    seed_full_board,
    set_territory_owner,
)

pytestmark = pytest.mark.regression


class PlayerAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.player = PlayerAgent("Alice", StubLLMClient())

    def test_parse_response_text_extracts_moves_reasoning_and_source(self):
        response = (
            "Move 1: |||Brazil, 3|||\n"
            "Move 2: |||Peru, 1|||\n"
            "From Territory:###Argentina###\n"
            "Reasoning:+++Push into South America+++"
        )

        moves, reasoning, from_territory = self.player.parse_response_text(response)

        self.assertEqual(
            moves,
            [
                {"territory_name": "Brazil", "num_troops": 3},
                {"territory_name": "Peru", "num_troops": 1},
            ],
        )
        self.assertEqual(reasoning, "Push into South America")
        self.assertEqual(from_territory, "Argentina")

    def test_parse_response_text_returns_empty_move_on_bad_format(self):
        moves, reasoning, from_territory = self.player.parse_response_text(
            "This is not in the expected Risk format."
        )

        self.assertEqual(moves, [{"territory_name": None, "num_troops": None}])
        self.assertIsNone(reasoning)
        self.assertIsNone(from_territory)

    def test_parse_card_trade_response_extracts_indices_and_reasoning(self):
        cards, reasoning = self.player.parse_card_trade_response(
            "Trade: |||1, 3, 4||| Reasoning:+++Best value now+++"
        )

        self.assertEqual(cards, [1, 3, 4])
        self.assertEqual(reasoning, "Best value now")

    def test_parse_response_strategy_truncates_long_text(self):
        parsed = self.player.parse_response_strategy("x" * 1500)

        self.assertEqual(len(parsed), 1200)

    def test_decision_log_records_strategy_prompt_response(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        client = RecordingLLMClient(response="- Reinforce Alaska.\n- Avoid weak attacks.")
        player = PlayerAgent("Alice", client)

        player.define_strategy_for_move(rules, game_state)

        decision_log = player.get_turn_decision_log()
        self.assertEqual(len(decision_log), 1)
        self.assertEqual(decision_log[0]["phase"], "pre_turn_planning")
        self.assertEqual(
            decision_log[0]["raw_response"],
            "- Reinforce Alaska.\n- Avoid weak attacks.",
        )
        self.assertEqual(player.turn_strategy, "- Reinforce Alaska.\n- Avoid weak attacks.")

    def test_initial_placement_uses_logged_fallback_response_on_llm_error(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        class FailingLLMClient(StubLLMClient):
            def get_chat_completion(self, messages) -> str:
                raise RuntimeError("simulated timeout")

        player = PlayerAgent("Alice", FailingLLMClient())

        moves, reasoning, _ = player.make_initial_troop_placement(rules, game_state)

        self.assertEqual(moves, [{"territory_name": "Blank", "num_troops": 0}])
        self.assertIn("LLM call failed", reasoning)
        decision_log = player.get_turn_decision_log()
        self.assertTrue(decision_log[0]["used_fallback_response"])
        self.assertIn("simulated timeout", decision_log[0]["error"])

    def test_attack_uses_skip_fallback_response_on_llm_error(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        class FailingLLMClient(StubLLMClient):
            def get_chat_completion(self, messages) -> str:
                raise RuntimeError("simulated timeout")

        player = PlayerAgent("Alice", FailingLLMClient())
        player.turn_strategy = "Press a weak border."

        moves, reasoning, from_territory = player.make_attack_move(
            rules,
            game_state,
            successful_attacks=0,
        )

        self.assertEqual(moves, [{"territory_name": "Blank", "num_troops": 0}])
        self.assertEqual(from_territory, "Blank")
        self.assertIn("LLM call failed", reasoning)
        self.assertTrue(player.get_turn_decision_log()[0]["used_fallback_response"])

    def test_mandatory_card_trade_uses_valid_fallback_combo_on_llm_error(self):
        _, game_state, _ = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        class FailingLLMClient(StubLLMClient):
            def get_chat_completion(self, messages) -> str:
                raise RuntimeError("simulated timeout")

        player = PlayerAgent("Alice", FailingLLMClient())
        cards = [
            SimpleNamespace(territory="Brazil", troop_type="infantry"),
            SimpleNamespace(territory="Peru", troop_type="cavalry"),
            SimpleNamespace(territory="Argentina", troop_type="artillery"),
        ]
        valid_combinations = {
            10: [([1, 2, 3], False)],
            8: [([1, 3, 2], False)],
        }

        selected_cards, reasoning = player.must_trade_cards(
            cards,
            game_state,
            valid_combinations,
        )

        self.assertEqual(selected_cards, [1, 2, 3])
        self.assertIn("LLM call failed", reasoning)
        self.assertTrue(player.get_turn_decision_log()[0]["used_fallback_response"])

    def test_troop_placement_uses_fast_placement_profile(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])
        target_territory = game_state.get_player_territories("Alice")[0]

        class OptionsCapturingLLMClient(StubLLMClient):
            def __init__(self, response: str) -> None:
                super().__init__()
                self.response = response
                self.last_kwargs = None

            def get_chat_completion(self, messages, **kwargs) -> str:
                self.last_kwargs = kwargs
                return self.response

        client = OptionsCapturingLLMClient(
            f"Move 1: |||{target_territory}, 3|||\n"
            "Reasoning:+++Reinforce the border.+++"
        )
        player = PlayerAgent("Alice", client)
        player.troops = 3
        player.placement_reasoning_effort = "low"
        player.placement_time_limit_seconds = 15

        moves, reasoning, _ = player.make_troop_placement(rules, game_state)

        self.assertEqual(moves, [{"territory_name": target_territory, "num_troops": 3}])
        self.assertEqual(reasoning, "Reinforce the border.")
        self.assertIsNone(client.last_kwargs)
        self.assertEqual(player.get_turn_decision_log()[0]["timeout_seconds"], 15)
        self.assertEqual(
            player.get_turn_decision_log()[0]["reasoning_effort_override"], "low"
        )

    def test_expired_turn_deadline_forces_fallback_response(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        player = PlayerAgent("Alice", StubLLMClient())
        player.turn_deadline = time.time() - 1

        moves, reasoning, from_territory = player.make_attack_move(
            rules,
            game_state,
            successful_attacks=0,
        )

        self.assertEqual(moves, [{"territory_name": "Blank", "num_troops": 0}])
        self.assertEqual(from_territory, "Blank")
        self.assertTrue(player.turn_time_exhausted)
        self.assertIn("expired", player.get_turn_decision_log()[0]["error"])

    def test_wall_clock_timeout_enforces_fast_placement_fallback(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        class SlowLLMClient(StubLLMClient):
            def get_chat_completion(self, messages, **kwargs) -> str:
                time.sleep(0.2)
                return "Move 1: |||Alaska, 3|||\nReasoning:+++Too slow+++"

        player = PlayerAgent("Alice", SlowLLMClient())
        player.troops = 3
        player.placement_time_limit_seconds = 0.05
        started = time.time()

        moves, reasoning, _ = player.make_troop_placement(rules, game_state)
        elapsed = time.time() - started

        self.assertLess(elapsed, 0.15)
        self.assertEqual(moves, [{"territory_name": "Blank", "num_troops": 0}])
        self.assertIn("LLM call failed", reasoning)
        self.assertTrue(player.get_turn_decision_log()[0]["used_fallback_response"])

    def test_non_placement_prompts_use_phase_reasoning_profiles(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        class OptionsCapturingLLMClient(StubLLMClient):
            def __init__(self, responses):
                super().__init__()
                self.responses = list(responses)
                self.recorded_kwargs = []

            def get_chat_completion(self, messages, **kwargs) -> str:
                self.recorded_kwargs.append(kwargs)
                return self.responses.pop(0)

        player = PlayerAgent(
            "Alice",
            OptionsCapturingLLMClient(
                [
                    "- Reinforce Alaska.\n- Attack Kamchatka if safe.",
                    "Attack Opponent Territory:|||Kamchatka, 3|||\n"
                    "From Territory:###Alaska###\n"
                    "Reasoning:+++Best border attack.+++",
                    "To Territory:|||Alaska, 2|||\n"
                    "From Territory:###Northwest Territory###\n"
                    "Reasoning:+++Reinforce the frontline.+++",
                    "||| 0 |||",
                ]
            ),
        )
        player.planning_reasoning_effort = "medium"
        player.attack_reasoning_effort = "medium"
        player.fortify_reasoning_effort = "low"
        player.card_trade_reasoning_effort = "low"
        player.turn_strategy = "Test plan"

        player.define_strategy_for_move(rules, game_state)
        player.make_attack_move(rules, game_state, successful_attacks=0)
        player.make_fortify_move(rules, game_state)
        player.may_trade_cards([], game_state, {})

        self.assertEqual(
            player.llm_client.recorded_kwargs,
            [
                {"reasoning_effort": "medium", "max_attempts_override": None},
                {"reasoning_effort": "medium", "max_attempts_override": None},
                {"reasoning_effort": "low", "max_attempts_override": None},
                {"reasoning_effort": "low", "max_attempts_override": None},
            ],
        )

    def test_openai_non_reasoning_model_drops_reasoning_override(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])
        target_territory = game_state.get_player_territories("Alice")[0]

        class OpenAINonReasoningClient(StubLLMClient):
            def __init__(self) -> None:
                super().__init__()
                self.provider_name = "OpenAI"
                self.model_type = "gpt-4.1"
                self.supports_reasoning = False
                self.last_kwargs = None

            def get_chat_completion(self, messages, **kwargs) -> str:
                self.last_kwargs = kwargs
                return (
                    f"Move 1: |||{target_territory}, 3|||\n"
                    "Reasoning:+++Use the legal territory list.+++"
                )

        client = OpenAINonReasoningClient()
        player = PlayerAgent("Alice", client)
        player.troops = 3
        player.placement_reasoning_effort = "low"
        player.placement_time_limit_seconds = 15

        moves, reasoning, _ = player.make_troop_placement(rules, game_state)

        self.assertEqual(moves, [{"territory_name": target_territory, "num_troops": 3}])
        self.assertEqual(reasoning, "Use the legal territory list.")
        self.assertIsNone(client.last_kwargs)
        self.assertEqual(
            player.get_turn_decision_log()[0]["reasoning_effort_override"],
            None,
        )

    def test_openai_reasoning_effort_is_raised_to_supported_floor(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])
        target_territory = game_state.get_player_territories("Alice")[0]

        class OpenAIReasoningClient(StubLLMClient):
            def __init__(self) -> None:
                super().__init__()
                self.provider_name = "OpenAI"
                self.model_type = "gpt-5.5-pro"
                self.supports_reasoning = True
                self.last_kwargs = None

            def supported_reasoning_efforts(self, model_name):
                if model_name != "gpt-5.5-pro":
                    raise AssertionError(model_name)
                return ("medium", "high", "xhigh")

            def get_chat_completion(self, messages, **kwargs) -> str:
                self.last_kwargs = kwargs
                return (
                    f"Move 1: |||{target_territory}, 3|||\n"
                    "Reasoning:+++Use the nearest supported reasoning level.+++"
                )

        client = OpenAIReasoningClient()
        player = PlayerAgent("Alice", client)
        player.troops = 3
        player.placement_reasoning_effort = "low"
        player.placement_time_limit_seconds = 15

        moves, reasoning, _ = player.make_troop_placement(rules, game_state)

        self.assertEqual(moves, [{"territory_name": target_territory, "num_troops": 3}])
        self.assertEqual(reasoning, "Use the nearest supported reasoning level.")
        self.assertIsNone(client.last_kwargs)
        self.assertEqual(
            player.get_turn_decision_log()[0]["reasoning_effort_override"],
            "medium",
        )

    def test_llm_interaction_logger_writes_prompt_and_response(self):
        _, game_state, rules = make_game_state("Alice", "Bob", "Carol")
        seed_full_board(game_state, ["Alice", "Bob", "Carol"])

        target_territory = game_state.get_player_territories("Alice")[0]

        class SimpleLLMClient(StubLLMClient):
            def get_chat_completion(self, messages, **kwargs) -> str:
                return (
                    f"Move 1: |||{target_territory}, 3|||\n"
                    "Reasoning:+++Reinforce the strongest border.+++"
                )

        player = PlayerAgent("Alice", SimpleLLMClient())
        player.troops = 3
        with tempfile.TemporaryDirectory() as temp_dir:
            player.configure_llm_interaction_logger(
                build_llm_interaction_logger(str(Path(temp_dir) / "game__test"))
            )
            player.set_interaction_context(game_round=2, turn_number=7, scope="turn")

            player.make_troop_placement(rules, game_state)

            interaction_files = sorted(
                Path(temp_dir, "llm_interactions", "game__test").rglob("*.json")
            )
            self.assertEqual(len(interaction_files), 1)
            payload = json.loads(interaction_files[0].read_text())
            self.assertEqual(payload["player"], "Alice")
            self.assertEqual(payload["phase"], "troop_placement")
            self.assertEqual(payload["turn_number"], 7)
            self.assertEqual(payload["scope"], "turn")
            self.assertEqual(payload["interaction_index"], 1)
            self.assertIn("Troop placement", payload["request"]["prompt"])
            self.assertIn(target_territory, payload["response"]["raw_response"])

            decision = player.get_turn_decision_log()[0]
            self.assertEqual(decision["interaction_index"], 1)
            self.assertEqual(decision["scope"], "turn")

    def test_initial_placement_prompt_includes_time_budget_and_final_check(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])

        client = RecordingLLMClient(
            response="Move:|||Alaska, 1|||\nReasoning:+++Fast border choice+++"
        )
        player = PlayerAgent("Alice", client)
        player.prompt_include_time_budget = True
        player.prompt_repeat_key_points = True
        player.placement_time_limit_seconds = 25
        player._call_llm_with_timeout = lambda message_content, **kwargs: (
            player.send_message(message_content, **kwargs)
        )

        player.make_initial_troop_placement(rules, game_state)

        self.assertIn("TIME BUDGET:", client.last_message)
        self.assertIn("Hard timeout for this decision: 25.000 seconds.", client.last_message)
        self.assertIn("FINAL CHECK:", client.last_message)
        self.assertIn("Choose exactly 1 legal territory you control.", client.last_message)

    def test_attack_prompt_includes_remaining_turn_time_and_usable_budget(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_state, "Kamchatka", "Bob", 1)

        client = RecordingLLMClient(
            response=(
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Stop+++"
            )
        )
        player = PlayerAgent("Alice", client)
        player.prompt_include_time_budget = True
        player.prompt_repeat_key_points = True
        player.turn_strategy = "Break through quickly."
        player.turn_deadline = time.time() + 123.456
        player._call_llm_with_timeout = lambda message_content, **kwargs: (
            player.send_message(message_content, **kwargs)
        )

        player.make_attack_move(rules, game_state, successful_attacks=2)

        self.assertIn("TIME BUDGET:", client.last_message)
        self.assertIn("Remaining total turn time right now:", client.last_message)
        self.assertIn("Usable turn time after the safety buffer:", client.last_message)
        self.assertIn("FINAL CHECK:", client.last_message)
        self.assertIn("If a fast favorable chain is available, keep the sequence moving.", client.last_message)
        self.assertRegex(client.last_message, r"Hard timeout for this decision: \d+\.\d{3} seconds\.")

    def test_attack_prompt_surfaces_planned_next_legal_attack(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Iceland", "Alice", 8)
        set_territory_owner(game_state, "Greenland", "Bob", 1)
        set_territory_owner(game_state, "Ontario", "Bob", 1)

        client = RecordingLLMClient(
            response=(
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Stop+++"
            )
        )
        player = PlayerAgent("Alice", client)
        player.turn_strategy = (
            "- Reinforce Iceland.\n"
            "- Fastest chain: Iceland -> Greenland -> Ontario."
        )
        player.turn_deadline = time.time() + 100
        player._call_llm_with_timeout = lambda message_content, **kwargs: (
            player.send_message(message_content, **kwargs)
        )

        player.make_attack_move(rules, game_state, successful_attacks=1)

        self.assertIn("PLAN EXECUTION:", client.last_message)
        self.assertIn(
            "Saved attack chain from your turn plan: Iceland -> Greenland -> Ontario.",
            client.last_message,
        )
        self.assertIn(
            "Planned next legal attack right now: step 1, Iceland -> Greenland",
            client.last_message,
        )
        self.assertIn(
            "Do not re-plan the whole board from scratch after every successful capture.",
            client.last_message,
        )

    def test_planning_prompt_requests_explicit_arrow_notation_for_breakthroughs(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])

        client = RecordingLLMClient(
            response="- Reinforce Iceland.\n- Iceland -> Greenland -> Ontario."
        )
        player = PlayerAgent("Alice", client)
        player.prompt_repeat_key_points = True
        player.turn_deadline = time.time() + 120
        player._call_llm_with_timeout = lambda message_content, **kwargs: (
            player.send_message(message_content, **kwargs)
        )

        player.define_strategy_for_move(rules, game_state)

        self.assertIn(
            "If you see a promising multi-step breakthrough, write it explicitly as `Territory -> Territory -> Territory`.",
            client.last_message,
        )
        self.assertIn(
            "If you name an attack chain, use explicit Territory -> Territory notation.",
            client.last_message,
        )

    def test_prompt_budget_and_final_check_can_be_disabled_for_probe_variants(self):
        _, game_state, rules = make_game_state("Alice", "Bob")
        seed_full_board(game_state, ["Alice", "Bob"])
        set_territory_owner(game_state, "Alaska", "Alice", 5)
        set_territory_owner(game_state, "Kamchatka", "Bob", 1)

        client = RecordingLLMClient(
            response=(
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++Stop+++"
            )
        )
        player = PlayerAgent("Alice", client)
        player.prompt_include_time_budget = False
        player.prompt_repeat_key_points = False
        player.turn_strategy = "Hold."
        player.turn_deadline = time.time() + 100
        player._call_llm_with_timeout = lambda message_content, **kwargs: (
            player.send_message(message_content, **kwargs)
        )

        player.make_attack_move(rules, game_state, successful_attacks=0)

        self.assertNotIn("TIME BUDGET:", client.last_message)
        self.assertNotIn("FINAL CHECK:", client.last_message)


if __name__ == "__main__":
    unittest.main()
