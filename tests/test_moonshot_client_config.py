from types import SimpleNamespace
from unittest.mock import patch

import pytest

from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.llm_clients.moonshot_client import MoonshotClient


pytestmark = pytest.mark.regression


class DummyMoonshotOpenAI:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs
        self.last_timeout = kwargs.get("timeout")
        self.last_params = None
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **params):
        self.last_params = params
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="stub-response")
                )
            ]
        )

    def with_options(self, **kwargs):
        if "timeout" in kwargs:
            self.last_timeout = kwargs["timeout"]
        return self


@patch.dict("os.environ", {"MOONSHOT_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.moonshot_client.OpenAI", DummyMoonshotOpenAI)
def test_moonshot_client_supports_current_model_names():
    kimi = MoonshotClient(model_name="kimi-k2.6")
    auto = MoonshotClient(model_name="moonshot-v1-auto")

    assert kimi.model_type == "kimi-k2.6"
    assert auto.model_type == "moonshot-v1-auto"


@patch.dict("os.environ", {"MOONSHOT_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.moonshot_client.OpenAI", DummyMoonshotOpenAI)
def test_moonshot_client_supports_legacy_numbers():
    assert MoonshotClient(model_number=1).model_type == "kimi-k2.6"
    assert MoonshotClient(model_number=6).model_type == "moonshot-v1-128k"


@patch.dict("os.environ", {"MOONSHOT_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.moonshot_client.OpenAI", DummyMoonshotOpenAI)
def test_moonshot_client_calls_openai_compatible_chat_api():
    client = MoonshotClient(model_name="kimi-k2.6", enable_thinking=False)

    response = client.get_chat_completion("test prompt", timeout_seconds=17)

    assert response == "stub-response"
    assert client.client.last_timeout == 17
    assert client.client.last_params["model"] == "kimi-k2.6"
    assert client.client.last_params["messages"][1]["content"] == "test prompt"
    assert client.client.last_params["extra_body"]["thinking"]["type"] == "disabled"


@patch.dict("os.environ", {"MOONSHOT_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.moonshot_client.OpenAI", DummyMoonshotOpenAI)
def test_llm_factory_accepts_moonshot_model_name_strings():
    client = create_llm_client("Moonshot", "kimi-k2.6", enable_thinking=True)

    assert isinstance(client, MoonshotClient)
    assert client.model_type == "kimi-k2.6"
    assert client.enable_thinking is True
