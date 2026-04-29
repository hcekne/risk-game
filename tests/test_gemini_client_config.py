from unittest.mock import patch

import pytest

from risk_game.llm_clients.gemini_client import GeminiClient
from risk_game.llm_clients.llm_client import create_llm_client


pytestmark = pytest.mark.regression


class DummyGeminiResponse:
    def __init__(self, payload):
        self.payload = payload
        self.text = '{"stub": true}'

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def _stub_post_factory(calls):
    def _post(url, headers, json, timeout):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return DummyGeminiResponse(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "stub-response"},
                            ]
                        }
                    }
                ]
            }
        )

    return _post


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
def test_gemini_client_supports_core_model_names():
    flash = GeminiClient(model_name="gemini-2.5-flash")
    pro = GeminiClient(model_name="gemini-3.1-pro-preview")
    prefixed = GeminiClient(model_name="models/gemini-3.1-pro-preview")

    assert flash.model_type == "gemini-2.5-flash"
    assert pro.model_type == "gemini-3.1-pro-preview"
    assert prefixed.model_type == "gemini-3.1-pro-preview"


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
def test_gemini_client_supports_legacy_numbers():
    assert GeminiClient(model_number=1).model_type == "gemini-2.5-pro"
    assert GeminiClient(model_number=4).model_type == "gemini-3.1-pro-preview"
    assert GeminiClient(model_number=5).model_type == "gemini-3.1-flash-lite-preview"


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.gemini_client.requests.post")
def test_gemini_client_builds_gemini3_thinking_level(mock_post):
    calls = []
    mock_post.side_effect = _stub_post_factory(calls)
    client = GeminiClient(model_name="gemini-3-flash-preview", reasoning_effort="high")

    response = client.get_chat_completion("test prompt", timeout_seconds=11)

    assert response == "stub-response"
    assert calls[0]["timeout"] == 11
    assert calls[0]["json"]["generationConfig"]["thinkingConfig"]["thinkingLevel"] == "high"


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.gemini_client.requests.post")
def test_gemini31_client_avoids_minimal_level_when_none_requested(mock_post):
    calls = []
    mock_post.side_effect = _stub_post_factory(calls)
    client = GeminiClient(model_name="gemini-3.1-pro-preview", reasoning_effort="none")

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert calls[0]["json"]["generationConfig"]["thinkingConfig"]["thinkingLevel"] == "low"


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.gemini_client.requests.post")
def test_gemini_client_builds_gemini25_budget(mock_post):
    calls = []
    mock_post.side_effect = _stub_post_factory(calls)
    client = GeminiClient(model_name="gemini-2.5-flash", reasoning_effort="low")

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert calls[0]["json"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 512


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("risk_game.llm_clients.gemini_client.requests.post")
def test_gemini_client_avoids_zero_budget_on_gemini25_pro(mock_post):
    calls = []
    mock_post.side_effect = _stub_post_factory(calls)
    client = GeminiClient(model_name="gemini-2.5-pro", reasoning_effort="none")

    response = client.get_chat_completion("test prompt")

    assert response == "stub-response"
    assert calls[0]["json"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 128


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
def test_llm_factory_accepts_gemini_model_name_strings():
    client = create_llm_client(
        "Gemini",
        "gemini-2.5-flash",
        reasoning_effort="medium",
    )

    assert isinstance(client, GeminiClient)
    assert client.model_type == "gemini-2.5-flash"
    assert client.reasoning_effort == "medium"
