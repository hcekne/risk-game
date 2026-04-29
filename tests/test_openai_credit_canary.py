import time

import pytest

from risk_game.llm_clients.openai_client import OpenAIClient


pytestmark = [pytest.mark.live_api, pytest.mark.credit_canary]


def test_openai_credit_canary_gpt54_nano():
    """
    Minimal paid OpenAI completion check.

    This is intentionally tiny and cheap, but it still proves that:
    - the API key is present
    - the account has usable quota/credits
    - a real billable completion can succeed
    """

    client = OpenAIClient(
        model_name="gpt-5.4-nano",
        use_responses_api=True,
        reasoning_effort="none",
        verbosity="low",
    )

    start = time.time()
    response = client.get_chat_completion(
        "Reply with exactly OK.",
        reasoning_effort="none",
        timeout_seconds=20,
        max_attempts_override=1,
    )
    elapsed = time.time() - start

    print(f"gpt-5.4-nano credit canary -> {elapsed:.2f}s, {len(response)} chars")
    assert response.strip().upper().startswith("OK")
