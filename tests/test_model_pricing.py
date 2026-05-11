import pytest

from risk_game.utils.model_pricing import (
    PRICING_SNAPSHOT_ID,
    estimate_usage_cost_usd,
    resolve_model_pricing,
)


pytestmark = pytest.mark.regression


def test_resolve_model_pricing_matches_exact_model_and_snapshot_suffixes():
    pricing = resolve_model_pricing("OpenAI", "gpt-5.1")
    snapshot_pricing = resolve_model_pricing("OpenAI", "gpt-5.1-2025-12-11")

    assert pricing is not None
    assert snapshot_pricing is not None
    assert pricing["pricing_snapshot_id"] == PRICING_SNAPSHOT_ID
    assert snapshot_pricing["input_usd_per_million_tokens"] == 1.25
    assert snapshot_pricing["output_usd_per_million_tokens"] == 10.0


def test_estimate_usage_cost_usd_accounts_for_cached_input_tokens():
    estimate = estimate_usage_cost_usd(
        provider="OpenAI",
        model="gpt-5.1",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "cached_input_tokens": 200,
        },
    )

    assert estimate is not None
    assert estimate["input_cost_usd"] == 0.001
    assert estimate["cached_input_cost_usd"] == 0.000025
    assert estimate["output_cost_usd"] == 0.005
    assert estimate["total_cost_usd"] == 0.006025


def test_estimate_usage_cost_usd_bills_gemini_reasoning_tokens_as_output():
    estimate = estimate_usage_cost_usd(
        provider="Gemini",
        model="gemini-3-flash-preview",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "reasoning_tokens": 250,
            "cached_input_tokens": 200,
        },
    )

    assert estimate is not None
    assert estimate["input_cost_usd"] == 0.0004
    assert estimate["cached_input_cost_usd"] == 0.00001
    assert estimate["output_cost_usd"] == 0.00225
    assert estimate["total_cost_usd"] == 0.00266
