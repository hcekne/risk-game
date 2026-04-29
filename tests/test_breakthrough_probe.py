import pytest

from risk_game.game_config import GameConfig
from risk_game.game_state import GameState
from risk_game.player_agent import PlayerAgent
from risk_game.rules import Rules
from scripts.probe_breakthrough_scenario import apply_variant, setup_breakthrough_scenario
from tests.helpers import StubLLMClient


pytestmark = pytest.mark.regression


def test_breakthrough_probe_scenario_has_single_clear_attack_source():
    rules = Rules(GameConfig())
    players = [
        PlayerAgent("Probe", StubLLMClient()),
        PlayerAgent("NorthAmerica", StubLLMClient()),
        PlayerAgent("Europe", StubLLMClient()),
        PlayerAgent("Asia", StubLLMClient()),
    ]
    game_state = GameState(players, rules)

    setup_breakthrough_scenario(game_state, "Probe")

    strong_territories = game_state.get_strong_territories_with_troops("Probe")
    assert strong_territories == [("Iceland", 29)]

    attack_vectors = game_state.get_adjacent_enemy_territories(
        "Probe", strong_territories
    )
    assert list(attack_vectors.keys()) == ["Iceland"]
    assert attack_vectors["Iceland"][1] == ["Greenland"]

    assert game_state.check_number_of_troops("Probe", "Great Britain") == 1
    assert game_state.check_number_of_troops("Probe", "Scandinavia") == 1
    assert game_state.check_number_of_troops("NorthAmerica", "Greenland") == 1
    assert game_state.check_number_of_troops("NorthAmerica", "Alaska") == 8


def test_probe_architecture_variants_toggle_system_prompt_and_handoff():
    player = PlayerAgent("Probe", StubLLMClient())
    assert player.llm_client.system_prompt_profile == "timed_risk_live"
    assert "competitive Risk agent" in player.llm_client.system_prompt

    apply_variant(player, "minimal_baseline")
    assert player.llm_client.system_prompt_profile == "minimal"
    assert player.prompt_include_time_budget is False
    assert player.prompt_repeat_key_points is False
    assert player.prompt_use_attack_plan_handoff is False

    apply_variant(player, "system_prompt_only")
    assert player.llm_client.system_prompt_profile == "timed_risk_live"
    assert player.prompt_include_time_budget is False
    assert player.prompt_repeat_key_points is False
    assert player.prompt_use_attack_plan_handoff is False

    apply_variant(player, "system_plus_execution_handoff")
    assert player.llm_client.system_prompt_profile == "timed_risk_live"
    assert player.prompt_include_time_budget is False
    assert player.prompt_repeat_key_points is False
    assert player.prompt_use_attack_plan_handoff is True
