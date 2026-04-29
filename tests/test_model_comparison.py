import time

import pytest

from risk_game.llm_clients.openai_client import OpenAIClient


pytestmark = pytest.mark.live_api


def test_gpt54_family_live_smoke():
    model_configs = [
        {"name": "gpt-5.4", "reasoning": "none"},
        {"name": "gpt-5.4-mini", "reasoning": "none"},
        {"name": "gpt-5.4-nano", "reasoning": "none"},
    ]

    prompt = (
        "You are playing Risk. In 35 words or fewer, explain whether taking "
        "a weak neighbor for card tempo can be correct even if it stretches "
        "your border."
    )

    for config in model_configs:
        client = OpenAIClient(
            model_name=config["name"],
            use_responses_api=True,
            reasoning_effort=config["reasoning"],
        )

        start = time.time()
        response = client.get_chat_completion(prompt)
        elapsed = time.time() - start

        print(
            f"{config['name']} ({config['reasoning']}) -> "
            f"{elapsed:.2f}s, {len(response)} chars"
        )
        assert response


def test_gpt54_nano_reasoning_modes_live_smoke():
    reasoning_efforts = ["none", "low", "medium", "high", "xhigh"]
    prompt = (
        "You are playing Risk. Return one sentence: when should a player stop "
        "attacking even if more legal attacks exist?"
    )

    for effort in reasoning_efforts:
        client = OpenAIClient(
            model_name="gpt-5.4-nano",
            use_responses_api=True,
            reasoning_effort=effort,
        )
        response = client.get_chat_completion(prompt)
        print(f"gpt-5.4-nano ({effort}) -> {len(response)} chars")
        assert response
