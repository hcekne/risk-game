import unittest

import pytest

from risk_game.utils.strategic_rubric import score_turn_summary


pytestmark = pytest.mark.regression


def make_turn_summary(
    *,
    plan_text: str,
    events: list[dict],
    derived: dict,
    pre_state: dict,
    post_state: dict,
) -> dict:
    return {
        "game_round": 1,
        "turn_number": 1,
        "player": {"name": "Alpha"},
        "plan": {"text": plan_text},
        "pre_turn": {"cards": 0, "player_state": pre_state},
        "post_turn": {"cards": derived["cards_delta"], "player_state": post_state},
        "derived": derived,
        "events": events,
    }


class StrategicRubricTests(unittest.TestCase):
    def test_rubric_scores_concrete_aligned_turn_as_strong(self):
        turn_summary = make_turn_summary(
            plan_text="Reinforce Brazil, attack Peru, then fortify North Africa.",
            events=[
                {
                    "phase": "troop_placement",
                    "attempt": 1,
                    "valid": True,
                    "outcome": "applied",
                    "moves": [{"territory_name": "Brazil", "num_troops": 4}],
                },
                {
                    "phase": "attack",
                    "attempt": 1,
                    "valid": True,
                    "outcome": "win",
                    "from_territory": "Brazil",
                    "target_territory": "Peru",
                    "attack_troops": 3,
                    "moves": [{"territory_name": "Peru", "num_troops": 3}],
                },
                {
                    "phase": "attack",
                    "attempt": 2,
                    "valid": True,
                    "outcome": "no_attack",
                    "from_territory": "Blank",
                    "target_territory": "Blank",
                    "attack_troops": 0,
                    "moves": [{"territory_name": "Blank", "num_troops": 0}],
                },
                {
                    "phase": "fortify",
                    "attempt": 1,
                    "valid": True,
                    "outcome": "applied",
                    "from_territory": "East Africa",
                    "to_territory": "North Africa",
                    "moved_troops": 2,
                    "moves": [{"territory_name": "North Africa", "num_troops": 2}],
                },
            ],
            derived={
                "territory_delta": 2,
                "troop_delta": 1,
                "cards_delta": 1,
                "new_continents": ["South America"],
                "lost_continents": [],
                "invalid_action_count": 0,
                "random_fallback_count": 0,
                "successful_attack_count": 1,
                "failed_attack_count": 0,
                "skipped_attack": True,
                "completed_card_trades": 0,
                "turn_time_seconds": 12.4,
            },
            pre_state={
                "territories": 12,
                "troops": 18,
                "continents": [],
                "territories_to_win": 16,
                "border_pressure": 7,
            },
            post_state={
                "territories": 14,
                "troops": 19,
                "continents": ["South America"],
                "territories_to_win": 14,
                "border_pressure": 8,
            },
        )

        rubric = score_turn_summary(turn_summary)

        self.assertEqual(rubric["band"], "strong")
        self.assertGreaterEqual(rubric["overall_score"], 4.0)
        self.assertEqual(rubric["dimensions"]["action_validity"]["score"], 5)
        self.assertGreaterEqual(rubric["dimensions"]["plan_alignment"]["score"], 4)
        self.assertGreaterEqual(rubric["dimensions"]["positional_outcome"]["score"], 4)

    def test_rubric_scores_invalid_unplanned_turn_as_weak(self):
        turn_summary = make_turn_summary(
            plan_text="",
            events=[
                {
                    "phase": "attack",
                    "attempt": 1,
                    "valid": False,
                    "outcome": "invalid",
                    "from_territory": "Brazil",
                    "target_territory": "Brazil",
                    "attack_troops": 5,
                    "error": "Already controls territory.",
                    "moves": [{"territory_name": "Brazil", "num_troops": 5}],
                },
                {
                    "phase": "troop_placement",
                    "attempt": 2,
                    "valid": True,
                    "outcome": "applied",
                    "fallback": True,
                    "moves": [{"territory_name": "Argentina", "num_troops": 3}],
                },
            ],
            derived={
                "territory_delta": -1,
                "troop_delta": -3,
                "cards_delta": 0,
                "new_continents": [],
                "lost_continents": ["South America"],
                "invalid_action_count": 2,
                "random_fallback_count": 1,
                "successful_attack_count": 0,
                "failed_attack_count": 1,
                "skipped_attack": False,
                "completed_card_trades": 0,
                "turn_time_seconds": 18.9,
            },
            pre_state={
                "territories": 13,
                "troops": 21,
                "continents": ["South America"],
                "territories_to_win": 15,
                "border_pressure": 6,
            },
            post_state={
                "territories": 12,
                "troops": 18,
                "continents": [],
                "territories_to_win": 16,
                "border_pressure": 10,
            },
        )

        rubric = score_turn_summary(turn_summary)

        self.assertEqual(rubric["band"], "weak")
        self.assertLessEqual(rubric["overall_score"], 2.5)
        self.assertEqual(rubric["dimensions"]["plan_concreteness"]["score"], 0)
        self.assertLessEqual(rubric["dimensions"]["action_validity"]["score"], 1)
        self.assertLessEqual(rubric["dimensions"]["positional_outcome"]["score"], 1)


if __name__ == "__main__":
    unittest.main()
