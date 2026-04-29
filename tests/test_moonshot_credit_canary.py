import time

import pytest

from risk_game.llm_clients.moonshot_client import MoonshotClient


pytestmark = [pytest.mark.live_api, pytest.mark.credit_canary]


def test_moonshot_credit_canary_kimi_k26():
    client = MoonshotClient(model_name="kimi-k2.6")

    start = time.time()
    response = client.get_chat_completion(
        "What is the capital of Norway? Reply with exactly one word.",
        timeout_seconds=45,
        max_attempts_override=1,
    )
    elapsed = time.time() - start

    print(
        f"kimi-k2.6 credit canary -> {elapsed:.2f}s, "
        f"{len(response)} chars, response={response.strip()!r}"
    )
    assert "OSLO" in response.strip().upper()
