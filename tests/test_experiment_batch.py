from pathlib import Path
from types import SimpleNamespace

import pytest

from risk_game.experiments import AgentSpec
from risk_game.game_config import GameConfig
from risk_game.game_master import GameMaster
from risk_game.rules import Rules
from risk_game.utils.experiment_batch import (
    build_series_manifest,
    build_experiment_manifest,
    build_status_line,
    combine_experiment_results,
    compute_experiment_summary,
    load_agent_specs,
    resolve_phase_reasoning_effort,
    rotate_agent_specs,
    run_agent_preflight,
)


pytestmark = pytest.mark.regression


def test_rotate_agent_specs_applies_cyclic_seat_rotation():
    specs = [
        AgentSpec(name="A", provider="OpenAI", model="gpt-5.5"),
        AgentSpec(name="B", provider="Anthropic", model="claude-opus-4-7"),
        AgentSpec(name="C", provider="Gemini", model="gemini-3.1-pro-preview"),
    ]

    rotated = rotate_agent_specs(specs, game_index=2)

    assert [spec.name for spec in rotated] == ["B", "C", "A"]


def test_load_agent_specs_reads_json_list(tmp_path: Path):
    payload = [
        {
            "name": "kimi",
            "provider": "Moonshot",
            "model": "kimi-k2.6",
            "enable_thinking": False,
            "planning_model": "kimi-k2.6",
            "planning_enable_thinking": True,
        }
    ]
    path = tmp_path / "agent_specs.json"
    path.write_text(__import__("json").dumps(payload))

    specs = load_agent_specs(str(path))

    assert len(specs) == 1
    assert specs[0].provider == "Moonshot"
    assert specs[0].model == "kimi-k2.6"
    assert specs[0].enable_thinking is False
    assert specs[0].planning_model == "kimi-k2.6"
    assert specs[0].planning_enable_thinking is True


def test_resolve_phase_reasoning_effort_caps_global_requests():
    assert resolve_phase_reasoning_effort("xhigh", None, "medium") == "medium"
    assert resolve_phase_reasoning_effort("medium", "low", "medium") == "low"


def test_compute_experiment_summary_aggregates_player_metrics():
    manifest = build_experiment_manifest(
        label="test-batch",
        preset_name="live_turn_frontier",
        num_games=2,
        config=GameConfig(),
        agent_specs=[
            AgentSpec(name="alpha", provider="OpenAI", model="gpt-5.5"),
            AgentSpec(name="beta", provider="Anthropic", model="claude-opus-4-7"),
        ],
        seat_rotation_enabled=True,
        base_folder="game_results/experiments",
    )
    results = [
        {
            "winner": "alpha",
            "victory_condition": "Territory Control 65%",
            "rounds": 5,
            "elapsed_seconds": 100.0,
            "territories": {"alpha": 28, "beta": 14},
            "turn_times": {"alpha": 40.0, "beta": 35.0},
            "strategic_scores": {"alpha": 4.5, "beta": 3.0},
            "llm_fallback_counts": {"alpha": 0, "beta": 1},
            "error_counts": {
                "alpha": {
                    "placement": 0,
                    "attack": 0,
                    "fortify": 0,
                    "card_trade": 0,
                    "formatting": 0,
                },
                "beta": {
                    "placement": 1,
                    "attack": 0,
                    "fortify": 0,
                    "card_trade": 0,
                    "formatting": 1,
                },
            },
            "game_folder": "game_results/experiments/exp/game__1",
        },
        {
            "winner": "beta",
            "victory_condition": "Territory Control 65%",
            "rounds": 7,
            "elapsed_seconds": 140.0,
            "territories": {"alpha": 12, "beta": 30},
            "turn_times": {"alpha": 52.0, "beta": 44.0},
            "strategic_scores": {"alpha": 3.4, "beta": 4.8},
            "llm_fallback_counts": {"alpha": 1, "beta": 0},
            "error_counts": {
                "alpha": {
                    "placement": 0,
                    "attack": 1,
                    "fortify": 0,
                    "card_trade": 0,
                    "formatting": 0,
                },
                "beta": {
                    "placement": 0,
                    "attack": 0,
                    "fortify": 1,
                    "card_trade": 0,
                    "formatting": 0,
                },
            },
            "game_folder": "game_results/experiments/exp/game__2",
        },
    ]

    summary = compute_experiment_summary(manifest, results)

    assert summary["num_games_completed"] == 2
    assert summary["mean_rounds"] == 6
    assert summary["win_counts"] == {"alpha": 1, "beta": 1}
    assert summary["players"]["alpha"]["mean_final_territories"] == 20
    assert summary["players"]["beta"]["mean_strategic_score"] == 3.9
    assert summary["players"]["beta"]["mean_fallback_count"] == 0.5


def test_build_status_line_is_compact_and_informative():
    line = build_status_line(
        {
            "label": "frontier",
            "state": "running",
            "completed_games": 2,
            "total_games": 15,
            "current_game_index": 3,
            "last_winner": "gpt-5.5",
            "error": None,
            "updated_at_utc": "2026-04-27T20:00:00Z",
        }
    )

    assert "frontier" in line
    assert "state=running" in line
    assert "games=2/15" in line
    assert "current=3" in line
    assert "last_winner=gpt-5.5" in line


def test_series_manifest_and_combined_results_preserve_stage_order(tmp_path: Path):
    config = GameConfig()
    agent_specs = [
        AgentSpec(name="gpt-5.5", provider="OpenAI", model="gpt-5.5"),
        AgentSpec(name="claude-opus-4-7", provider="Anthropic", model="claude-opus-4-7"),
    ]
    stage_one = {
        "experiment_folder": tmp_path / "stage_one",
        "manifest": build_experiment_manifest(
            label="frontier_stage_1",
            preset_name="live_turn_frontier",
            num_games=4,
            config=config,
            agent_specs=agent_specs,
            seat_rotation_enabled=True,
            base_folder="game_results/experiments",
        ),
        "results": [
            {"game_index": 1, "winner": "gpt-5.5", "game_folder": "g1"},
            {"game_index": 2, "winner": "claude-opus-4-7", "game_folder": "g2"},
        ],
    }
    stage_two = {
        "experiment_folder": tmp_path / "stage_two",
        "manifest": build_experiment_manifest(
            label="frontier_stage_2",
            preset_name="live_turn_frontier",
            num_games=12,
            config=config,
            agent_specs=agent_specs,
            seat_rotation_enabled=True,
            base_folder="game_results/experiments",
        ),
        "results": [
            {"game_index": 1, "winner": "gpt-5.5", "game_folder": "g3"},
        ],
    }

    combined_manifest = build_series_manifest(
        label="frontier_combined",
        contexts=[stage_one, stage_two],
    )
    combined_results = combine_experiment_results([stage_one, stage_two])

    assert combined_manifest["num_games"] == 16
    assert len(combined_manifest["source_experiments"]) == 2
    assert [result["game_index"] for result in combined_results] == [1, 2, 3]
    assert [result["source_game_index"] for result in combined_results] == [1, 2, 1]
    assert combined_results[2]["source_experiment_folder"].endswith("stage_two")


def test_game_master_applies_player_runtime_overrides():
    game = GameMaster(Rules(GameConfig()))
    dummy_llm = SimpleNamespace(provider_name="OpenAI", model_type="gpt-5.4-mini")
    planning_llm = SimpleNamespace(provider_name="OpenAI", model_type="gpt-5.5")

    game.add_player(
        name="mini-high",
        llm_client=dummy_llm,
        planning_llm_client=planning_llm,
        runtime_overrides={
            "turn_time_limit_seconds": 120,
            "planning_time_limit_seconds": 60,
            "placement_time_limit_seconds": 25,
            "placement_reasoning_effort": "high",
            "planning_reasoning_effort": "high",
            "attack_reasoning_effort": "high",
            "fortify_reasoning_effort": "high",
            "card_trade_reasoning_effort": "high",
        },
    )

    player = game.players[0]

    assert player.planning_llm_client is planning_llm
    assert player.turn_time_limit_seconds == 120
    assert player.planning_time_limit_seconds == 60
    assert player.placement_time_limit_seconds == 25
    assert player.placement_reasoning_effort == "high"
    assert player.planning_reasoning_effort == "high"
    assert player.attack_reasoning_effort == "high"
    assert player.fortify_reasoning_effort == "high"
    assert player.card_trade_reasoning_effort == "high"


def test_run_agent_preflight_checks_primary_and_planning_clients(monkeypatch):
    recorded_calls = []

    class DummyClient:
        def __init__(self, provider, model):
            self.provider = provider
            self.model = model

        def get_chat_completion(self, *args, **kwargs):
            return f"OK {self.provider} {self.model}"

    def fake_create_llm_client(provider, model, **kwargs):
        recorded_calls.append((provider, model, kwargs))
        return DummyClient(provider, model)

    monkeypatch.setattr(
        "risk_game.utils.experiment_batch.create_llm_client",
        fake_create_llm_client,
    )

    results = run_agent_preflight(
        [
            AgentSpec(
                name="openai-split",
                provider="OpenAI",
                model="gpt-5.4",
                planning_provider="OpenAI",
                planning_model="gpt-5.5",
            )
        ],
        timeout_seconds=5.0,
    )

    assert [call[:2] for call in recorded_calls] == [
        ("OpenAI", "gpt-5.4"),
        ("OpenAI", "gpt-5.5"),
    ]
    assert [result["client_role"] for result in results] == ["primary", "planning"]
