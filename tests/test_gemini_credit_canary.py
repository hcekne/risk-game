import time

import pytest

from risk_game.llm_clients.gemini_client import GeminiClient


pytestmark = [pytest.mark.live_api, pytest.mark.credit_canary]


def test_gemini_credit_canary_gemini31_pro_preview():
    client = GeminiClient(
        model_name="gemini-3.1-pro-preview",
        reasoning_effort="none",
    )

    start = time.time()
    response = client.get_chat_completion(
        "What is the capital of Norway? Reply with exactly one word.",
        reasoning_effort="none",
        timeout_seconds=45,
        max_attempts_override=1,
    )
    elapsed = time.time() - start

    print(
        "gemini-3.1-pro-preview credit canary -> "
        f"{elapsed:.2f}s, {len(response)} chars, response={response.strip()!r}"
    )
    assert "OSLO" in response.strip().upper()
