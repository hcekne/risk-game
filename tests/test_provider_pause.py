from pathlib import Path

import pytest

from risk_game.game_config import GameConfig
from risk_game.utils.experiment_batch import build_experiment_manifest
from risk_game.utils.provider_pause import (
    ExperimentPauseController,
    ProviderPauseAborted,
    detect_provider_pause_signal,
)


pytestmark = pytest.mark.regression


def test_detect_provider_pause_signal_matches_known_billing_errors():
    signal = detect_provider_pause_signal(
        "AnthropicError: Your credit balance is too low to access the Anthropic API."
    )

    assert signal is not None
    assert signal.category == "billing_or_quota"
    assert signal.matched_substring == "credit balance is too low"


def test_detect_provider_pause_signal_ignores_generic_timeout_errors():
    assert (
        detect_provider_pause_signal(
            "TimeoutError: Wall-clock timeout exceeded 15.00 seconds."
        )
        is None
    )


def test_pause_controller_records_pause_and_resume(tmp_path: Path):
    manifest = build_experiment_manifest(
        label="pause-test",
        preset_name=None,
        num_games=4,
        config=GameConfig(),
        agent_specs=[],
        seat_rotation_enabled=True,
        base_folder=str(tmp_path),
    )
    controller = ExperimentPauseController(
        experiment_folder=tmp_path,
        manifest=manifest,
        input_func=lambda prompt: "",
    )
    signal = detect_provider_pause_signal(
        "RateLimitError: quota exceeded {'error': {'code': 'insufficient_quota'}}"
    )
    assert signal is not None

    controller.pause_for_provider_issue(
        signal=signal,
        provider="OpenAI",
        model="gpt-5.1",
        player_name="gpt-5.1",
        phase="attack",
        client_role="primary",
        scope="turn",
        completed_games=2,
        current_game_index=3,
        current_seat_order=["gpt-5.1", "claude-opus-4-7"],
        last_completed_game_folder="/tmp/game__2",
        last_winner="gpt-5.1",
    )

    pause_events_path = tmp_path / "experiment_pause_events.json"
    status_path = tmp_path / "experiment_status.json"
    assert pause_events_path.exists()
    assert status_path.exists()

    events = __import__("json").loads(pause_events_path.read_text())["events"]
    status = __import__("json").loads(status_path.read_text())
    assert len(events) == 1
    assert events[0]["provider"] == "OpenAI"
    assert events[0]["resumed_at_utc"] is not None
    assert status["state"] == "running"
    assert status["completed_games"] == 2


def test_pause_controller_can_abort(tmp_path: Path):
    manifest = build_experiment_manifest(
        label="pause-test",
        preset_name=None,
        num_games=4,
        config=GameConfig(),
        agent_specs=[],
        seat_rotation_enabled=True,
        base_folder=str(tmp_path),
    )
    controller = ExperimentPauseController(
        experiment_folder=tmp_path,
        manifest=manifest,
        input_func=lambda prompt: "abort",
    )
    signal = detect_provider_pause_signal(
        "AnthropicError: Your credit balance is too low to access the Anthropic API."
    )
    assert signal is not None

    with pytest.raises(ProviderPauseAborted):
        controller.pause_for_provider_issue(
            signal=signal,
            provider="Anthropic",
            model="claude-opus-4-7",
            player_name="claude-opus-4-7",
            phase="preflight",
            client_role="primary",
            scope="preflight",
            completed_games=0,
            current_game_index=None,
            current_seat_order=None,
            last_completed_game_folder=None,
            last_winner=None,
        )
