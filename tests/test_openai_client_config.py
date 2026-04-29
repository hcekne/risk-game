from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from openai import APITimeoutError, RateLimitError

from risk_game.experiments import Experiment, build_openai_nano_reasoning_arena
from risk_game.game_config import GameConfig
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.llm_clients.openai_client import OpenAIClient


pytestmark = pytest.mark.regression


class DummyResponsesAPI:
    def __init__(self) -> None:
        self.last_params = None

    def create(self, **params):
        self.last_params = params
        return SimpleNamespace(output_text="stub-response")


class DummyOpenAI:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs
        self.last_timeout = kwargs.get("timeout")
        self.responses = DummyResponsesAPI()
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="stub"))]
                )
            )
        )

    def with_options(self, **kwargs):
        if "timeout" in kwargs:
            self.last_timeout = kwargs["timeout"]
        return self


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_supports_gpt54_family_by_model_name():
    flagship = OpenAIClient(model_name="gpt-5.4")
    mini = OpenAIClient(model_name="gpt-5.4-mini")
    nano = OpenAIClient(model_name="gpt-5.4-nano")

    assert flagship.model_type == "gpt-5.4"
    assert mini.model_type == "gpt-5.4-mini"
    assert nano.model_type == "gpt-5.4-nano"
    assert nano.reasoning_effort == "none"


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_supports_current_broader_model_catalog():
    clients = [
        OpenAIClient(model_name="gpt-5.5", reasoning_effort="xhigh"),
        OpenAIClient(model_name="gpt-5.4-pro", reasoning_effort="medium"),
        OpenAIClient(model_name="gpt-5-mini", reasoning_effort="minimal"),
        OpenAIClient(model_name="gpt-5-pro", reasoning_effort="high"),
        OpenAIClient(model_name="gpt-4.1-mini"),
        OpenAIClient(model_name="gpt-4o"),
        OpenAIClient(model_name="o3", reasoning_effort="medium"),
        OpenAIClient(model_name="o4-mini", reasoning_effort="high"),
    ]

    assert [client.model_type for client in clients] == [
        "gpt-5.5",
        "gpt-5.4-pro",
        "gpt-5-mini",
        "gpt-5-pro",
        "gpt-4.1-mini",
        "gpt-4o",
        "o3",
        "o4-mini",
    ]


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_supports_snapshot_model_ids():
    clients = [
        OpenAIClient(model_name="gpt-5.5-2026-04-23", reasoning_effort="high"),
        OpenAIClient(model_name="gpt-5.4-mini-2026-03-17", reasoning_effort="low"),
        OpenAIClient(model_name="gpt-4.1-2025-04-14"),
        OpenAIClient(model_name="o3-2025-04-16", reasoning_effort="medium"),
    ]

    assert [client.model_type for client in clients] == [
        "gpt-5.5-2026-04-23",
        "gpt-5.4-mini-2026-03-17",
        "gpt-4.1-2025-04-14",
        "o3-2025-04-16",
    ]


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_legacy_numbers_map_to_gpt54_family():
    assert OpenAIClient(model_number=1).model_type == "gpt-5.4"
    assert OpenAIClient(model_number=2).model_type == "gpt-5.4-mini"
    assert OpenAIClient(model_number=3).model_type == "gpt-5.4-nano"


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_rejects_invalid_reasoning_effort():
    with pytest.raises(ValueError, match="Invalid reasoning_effort"):
        OpenAIClient(model_name="gpt-5.4-nano", reasoning_effort="minimal")


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_rejects_disallowed_reasoning_on_non_reasoning_models():
    with pytest.raises(ValueError, match="does not support reasoning_effort"):
        OpenAIClient(model_name="gpt-4o", reasoning_effort="low")


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_enforces_model_specific_reasoning_tables():
    with pytest.raises(ValueError, match="Choose from \\['medium', 'high', 'xhigh'\\]"):
        OpenAIClient(model_name="gpt-5.5-pro", reasoning_effort="none")

    with pytest.raises(ValueError, match="Choose from \\['high'\\]"):
        OpenAIClient(model_name="gpt-5-pro", reasoning_effort="medium")

    client_55_pro = OpenAIClient(model_name="gpt-5.5-pro", reasoning_effort="medium")
    client = OpenAIClient(model_name="gpt-5-pro", reasoning_effort="high")

    assert client_55_pro.reasoning_effort == "medium"
    assert client.reasoning_effort == "high"


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_passes_reasoning_and_verbosity_to_responses_api():
    client = OpenAIClient(
        model_name="gpt-5.4-nano",
        reasoning_effort="low",
        verbosity="medium",
    )

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert client.client.responses.last_params["model"] == "gpt-5.4-nano"
    assert client.client.responses.last_params["reasoning"] == {"effort": "low"}
    assert client.client.responses.last_params["text"] == {"verbosity": "medium"}


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_allows_per_call_reasoning_and_timeout_overrides():
    client = OpenAIClient(
        model_name="gpt-5.4",
        reasoning_effort="xhigh",
        verbosity="low",
    )

    response = client.get_chat_completion(
        "test prompt",
        reasoning_effort="low",
        timeout_seconds=12,
    )

    assert response == "stub-response"
    assert client.client.last_timeout == 12
    assert client.client.responses.last_params["reasoning"] == {"effort": "low"}


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_openai_client_sets_long_timeout_by_default():
    client = OpenAIClient(model_name="gpt-5.4")

    assert client.timeout_seconds == OpenAIClient.DEFAULT_TIMEOUT_SECONDS
    assert client.client.kwargs["timeout"] == OpenAIClient.DEFAULT_TIMEOUT_SECONDS
    assert client.max_retries == 2


class TimeoutThenSuccessResponsesAPI:
    def __init__(self) -> None:
        self.calls = 0

    def create(self, **params):
        self.calls += 1
        if self.calls == 1:
            raise APITimeoutError(
                request=httpx.Request("POST", "https://api.openai.com/v1/responses")
            )
        return SimpleNamespace(output_text="recovered-response")


class TimeoutThenSuccessOpenAI:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs
        self.responses = TimeoutThenSuccessResponsesAPI()
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="stub"))]
                )
            )
        )


@patch("risk_game.llm_clients.openai_client.time.sleep", lambda *_: None)
@patch("risk_game.llm_clients.openai_client.OpenAI", TimeoutThenSuccessOpenAI)
def test_openai_client_retries_timeout_and_recovers():
    client = OpenAIClient(model_name="gpt-5.4-mini", reasoning_effort="xhigh")

    response = client.get_chat_completion("test prompt")

    assert response == "recovered-response"
    assert client.client.responses.calls == 2


@patch("risk_game.llm_clients.openai_client.time.sleep", lambda *_: None)
@patch("risk_game.llm_clients.openai_client.OpenAI", TimeoutThenSuccessOpenAI)
def test_openai_client_respects_single_attempt_override():
    client = OpenAIClient(model_name="gpt-5.4-mini", reasoning_effort="xhigh")

    with pytest.raises(RuntimeError, match="APITimeoutError"):
        client.get_chat_completion("test prompt", max_attempts_override=1)

    assert client.client.responses.calls == 1


class AlwaysRateLimitedResponsesAPI:
    def create(self, **params):
        raise RateLimitError(
            "quota exceeded",
            response=httpx.Response(
                429,
                request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
            ),
            body={"error": {"code": "insufficient_quota"}},
        )


class AlwaysRateLimitedOpenAI:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs
        self.responses = AlwaysRateLimitedResponsesAPI()
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="stub"))]
                )
            )
        )

    def with_options(self, **kwargs):
        return self


@patch("risk_game.llm_clients.openai_client.OpenAI", AlwaysRateLimitedOpenAI)
def test_openai_client_includes_provider_error_details_after_final_failure():
    client = OpenAIClient(model_name="gpt-5.4-nano", reasoning_effort="medium")

    with pytest.raises(RuntimeError, match="RateLimitError: quota exceeded"):
        client.get_chat_completion("test prompt", max_attempts_override=1)


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_llm_factory_accepts_openai_model_name_strings():
    client = create_llm_client(
        "OpenAI",
        "gpt-5.5",
        reasoning_effort="xhigh",
    )

    assert isinstance(client, OpenAIClient)
    assert client.model_type == "gpt-5.5"
    assert client.reasoning_effort == "xhigh"


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_experiment_can_build_gpt54_nano_reasoning_arena():
    experiment = Experiment(
        config=GameConfig(progressive=True, capitals=False, max_rounds=1),
        num_games=1,
        agent_specs=build_openai_nano_reasoning_arena(),
    )

    game = experiment.initialize_game()

    assert len(game.players) == 4
    assert [player.name for player in game.players] == [
        "gpt-5.4-nano-none",
        "gpt-5.4-nano-low",
        "gpt-5.4-nano-medium",
        "gpt-5.4-nano-high",
    ]
    assert all(player.llm_client.model_type == "gpt-5.4-nano" for player in game.players)


@patch("risk_game.llm_clients.openai_client.OpenAI", DummyOpenAI)
def test_game_config_phase_reasoning_profiles_flow_into_initialized_players():
    experiment = Experiment(
        config=GameConfig(
            progressive=True,
            capitals=False,
            max_rounds=1,
            planning_reasoning_effort="low",
            attack_reasoning_effort="medium",
            fortify_reasoning_effort="low",
            card_trade_reasoning_effort="low",
        ),
        num_games=1,
        agent_specs=build_openai_nano_reasoning_arena(),
    )

    game = experiment.initialize_game()
    game.init_game_state()

    for player in game.players:
        assert player.planning_reasoning_effort == "low"
        assert player.attack_reasoning_effort == "medium"
        assert player.fortify_reasoning_effort == "low"
        assert player.card_trade_reasoning_effort == "low"
