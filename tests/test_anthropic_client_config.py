from types import SimpleNamespace
from unittest.mock import patch

import pytest

from risk_game.llm_clients.anthropic_client import AnthropicClient
from risk_game.llm_clients.llm_client import create_llm_client


pytestmark = pytest.mark.regression


class DummyAnthropic:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs
        self.last_timeout = kwargs.get("timeout")
        self.last_params = None
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **params):
        self.last_params = params
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="thinking", thinking="hidden"),
                SimpleNamespace(type="text", text="stub-response"),
            ]
        )

    def with_options(self, **kwargs):
        if "timeout" in kwargs:
            self.last_timeout = kwargs["timeout"]
        return self


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_anthropic_client_supports_current_model_names():
    opus = AnthropicClient(model_name="claude-opus-4-7")
    sonnet = AnthropicClient(model_name="claude-sonnet-4-6")
    haiku = AnthropicClient(model_name="claude-haiku-4-5-20251001")

    assert opus.model_type == "claude-opus-4-7"
    assert opus.model_config.supports_temperature is False
    assert sonnet.model_type == "claude-sonnet-4-6"
    assert haiku.model_type == "claude-haiku-4-5-20251001"


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_anthropic_client_supports_legacy_alias_mapping():
    client = AnthropicClient(model_name="claude-sonnet-4-0")

    assert client.model_type == "claude-sonnet-4-20250514"


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_anthropic_client_uses_adaptive_thinking_when_supported():
    client = AnthropicClient(
        model_name="claude-opus-4-7",
        enable_thinking=True,
        thinking_effort="high",
    )

    response = client.get_chat_completion("test prompt", timeout_seconds=17)

    assert response == "stub-response"
    assert client.client.last_timeout == 17
    assert client.client.last_params["thinking"] == {
        "type": "adaptive",
        "display": "omitted",
    }
    assert client.client.last_params["max_tokens"] == 4000
    assert "temperature" not in client.client.last_params


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_non_opus_anthropic_models_still_set_temperature():
    client = AnthropicClient(
        model_name="claude-sonnet-4-6",
        enable_thinking=True,
        thinking_effort="medium",
    )

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert client.client.last_params["temperature"] == 1
    assert client.client.last_params["thinking"] == {
        "type": "adaptive",
        "effort": "medium",
        "display": "omitted",
    }


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_anthropic_client_maps_reasoning_effort_to_manual_thinking_budget():
    client = AnthropicClient(
        model_name="claude-sonnet-4-5-20250929",
        enable_thinking=True,
        thinking_budget=3000,
    )

    response = client.get_chat_completion("test prompt", reasoning_effort="xhigh")

    assert response == "stub-response"
    assert client.client.last_params["thinking"] == {
        "type": "enabled",
        "budget_tokens": 24000,
        "display": "omitted",
    }
    assert client.client.last_params["max_tokens"] == 24512


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_legacy_manual_thinking_snapshots_raise_max_tokens_above_budget():
    client = AnthropicClient(
        model_name="claude-opus-4-20250514",
        enable_thinking=True,
        thinking_budget=2000,
    )

    response = client.get_chat_completion("test prompt", reasoning_effort="medium")

    assert response == "stub-response"
    assert client.client.last_params["thinking"] == {
        "type": "enabled",
        "budget_tokens": 4096,
        "display": "omitted",
    }
    assert client.client.last_params["max_tokens"] == 4608


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_manual_thinking_uses_custom_budget_when_no_override_is_passed():
    client = AnthropicClient(
        model_name="claude-opus-4-20250514",
        enable_thinking=True,
        thinking_budget=5000,
    )

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert client.client.last_params["thinking"] == {
        "type": "enabled",
        "budget_tokens": 5000,
        "display": "omitted",
    }
    assert client.client.last_params["max_tokens"] == 5512


@patch("risk_game.llm_clients.anthropic_client.Anthropic", DummyAnthropic)
def test_llm_factory_accepts_anthropic_model_name_strings():
    client = create_llm_client(
        "Anthropic",
        "claude-sonnet-4-6",
        enable_thinking=True,
        thinking_effort="medium",
    )

    assert isinstance(client, AnthropicClient)
    assert client.model_type == "claude-sonnet-4-6"
    assert client.enable_thinking is True
    assert client.thinking_effort == "medium"
