import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from risk_game.game_config import GameConfig
from risk_game.game_master import GameMaster
from risk_game.rules import Rules
from risk_game.utils.game_admin import build_game_manifest, save_game_manifest
from tests.helpers import make_game_master


pytestmark = pytest.mark.regression


def test_game_manifest_captures_rules_and_player_models():
    game_master = make_game_master(
        "Alice",
        "Bob",
        progressive=True,
        capitals=False,
        max_rounds=12,
        turn_time_limit_seconds=90,
        placement_time_limit_seconds=15,
    )

    manifest = build_game_manifest(
        game_master,
        "/tmp/game__test",
        include_initial_troop_placement=True,
    )

    assert manifest["include_initial_troop_placement"] is True
    assert manifest["rules"]["max_rounds"] == 12
    assert manifest["rules"]["turn_time_limit_seconds"] == 90
    assert manifest["rules"]["placement_time_limit_seconds"] == 15
    assert sorted(player["name"] for player in manifest["players"]) == ["Alice", "Bob"]
    assert {player["provider"] for player in manifest["players"]} == {"stub"}
    assert {player["model"] for player in manifest["players"]} == {"stub"}


def test_save_game_manifest_writes_json_file():
    game_master = make_game_master("Alice", "Bob")

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = save_game_manifest(
            game_master,
            temp_dir,
            include_initial_troop_placement=False,
        )

        payload = json.loads(Path(output_path).read_text())
        assert payload["game_folder"] == Path(temp_dir).name
        assert payload["include_initial_troop_placement"] is False
        assert len(payload["players"]) == 2


def test_game_manifest_includes_planning_client_when_present():
    game_master = GameMaster(Rules(GameConfig()))
    game_master.add_player(
        "Alice",
        SimpleNamespace(
            provider_name="OpenAI",
            model_type="gpt-5.4",
            reasoning_effort="medium",
            verbosity="low",
        ),
        planning_llm_client=SimpleNamespace(
            provider_name="OpenAI",
            model_type="gpt-5.5",
            reasoning_effort="high",
            verbosity="low",
        ),
    )
    game_master.add_player("Bob", SimpleNamespace(provider_name="stub", model_type="stub"))

    manifest = build_game_manifest(
        game_master,
        "/tmp/game__planning_manifest",
        include_initial_troop_placement=False,
    )

    alice_entry = next(player for player in manifest["players"] if player["name"] == "Alice")
    assert alice_entry["planning_client"]["provider"] == "OpenAI"
    assert alice_entry["planning_client"]["model"] == "gpt-5.5"
    assert alice_entry["planning_client"]["reasoning_effort"] == "high"
