from __future__ import annotations

from typing import Any, Dict, Optional


PRICING_SNAPSHOT_ID = "2026-05-06"

PRICING_SOURCES = {
    "OpenAI": "https://platform.openai.com/docs/pricing",
    "Anthropic": "https://www.anthropic.com/claude/opus",
    "Anthropic_family": "https://docs.anthropic.com/en/docs/models-overview",
    "Gemini": "https://ai.google.dev/gemini-api/docs/pricing",
    "Moonshot": "https://platform.moonshot.ai/",
}


MODEL_PRICING: Dict[str, Dict[str, Dict[str, Any]]] = {
    "OpenAI": {
        "gpt-5.5": {
            "input_usd_per_million_tokens": 5.0,
            "cached_input_usd_per_million_tokens": 0.5,
            "output_usd_per_million_tokens": 30.0,
            "source": PRICING_SOURCES["OpenAI"],
        },
        "gpt-5.4": {
            "input_usd_per_million_tokens": 2.5,
            "cached_input_usd_per_million_tokens": 0.25,
            "output_usd_per_million_tokens": 15.0,
            "source": PRICING_SOURCES["OpenAI"],
        },
        "gpt-5.4-mini": {
            "input_usd_per_million_tokens": 0.75,
            "cached_input_usd_per_million_tokens": 0.075,
            "output_usd_per_million_tokens": 4.5,
            "source": PRICING_SOURCES["OpenAI"],
        },
        "gpt-5.2": {
            "input_usd_per_million_tokens": 1.75,
            "cached_input_usd_per_million_tokens": 0.175,
            "output_usd_per_million_tokens": 14.0,
            "source": PRICING_SOURCES["OpenAI"],
        },
        "gpt-5.1": {
            "input_usd_per_million_tokens": 1.25,
            "cached_input_usd_per_million_tokens": 0.125,
            "output_usd_per_million_tokens": 10.0,
            "source": PRICING_SOURCES["OpenAI"],
        },
        "gpt-4.1": {
            "input_usd_per_million_tokens": 2.0,
            "cached_input_usd_per_million_tokens": 0.5,
            "output_usd_per_million_tokens": 8.0,
            "source": PRICING_SOURCES["OpenAI"],
        },
    },
    "Anthropic": {
        "claude-opus-4-7": {
            "input_usd_per_million_tokens": 5.0,
            "output_usd_per_million_tokens": 25.0,
            "source": PRICING_SOURCES["Anthropic"],
        },
        "claude-opus-4-6": {
            "input_usd_per_million_tokens": 15.0,
            "cached_input_usd_per_million_tokens": 1.5,
            "output_usd_per_million_tokens": 75.0,
            "source": PRICING_SOURCES["Anthropic_family"],
        },
        "claude-opus-4-1-20250805": {
            "input_usd_per_million_tokens": 15.0,
            "cached_input_usd_per_million_tokens": 1.5,
            "output_usd_per_million_tokens": 75.0,
            "source": PRICING_SOURCES["Anthropic_family"],
        },
        "claude-opus-4-20250514": {
            "input_usd_per_million_tokens": 15.0,
            "cached_input_usd_per_million_tokens": 1.5,
            "output_usd_per_million_tokens": 75.0,
            "source": PRICING_SOURCES["Anthropic_family"],
        },
        "claude-sonnet-4-6": {
            "input_usd_per_million_tokens": 3.0,
            "cached_input_usd_per_million_tokens": 0.3,
            "output_usd_per_million_tokens": 15.0,
            "source": PRICING_SOURCES["Anthropic_family"],
        },
        "claude-sonnet-4-20250514": {
            "input_usd_per_million_tokens": 3.0,
            "cached_input_usd_per_million_tokens": 0.3,
            "output_usd_per_million_tokens": 15.0,
            "source": PRICING_SOURCES["Anthropic_family"],
        },
    },
    "Gemini": {
        "gemini-3.1-pro-preview": {
            "input_usd_per_million_tokens": 2.0,
            "cached_input_usd_per_million_tokens": 0.2,
            "output_usd_per_million_tokens": 12.0,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-3-pro-preview": {
            "input_usd_per_million_tokens": 2.0,
            "cached_input_usd_per_million_tokens": 0.2,
            "output_usd_per_million_tokens": 12.0,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-3-flash-preview": {
            "input_usd_per_million_tokens": 0.5,
            "cached_input_usd_per_million_tokens": 0.05,
            "output_usd_per_million_tokens": 3.0,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-3.1-flash-lite-preview": {
            "input_usd_per_million_tokens": 0.25,
            "cached_input_usd_per_million_tokens": 0.025,
            "output_usd_per_million_tokens": 1.5,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-2.5-pro": {
            "input_usd_per_million_tokens": 1.25,
            "cached_input_usd_per_million_tokens": 0.125,
            "output_usd_per_million_tokens": 10.0,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-2.5-flash": {
            "input_usd_per_million_tokens": 0.3,
            "cached_input_usd_per_million_tokens": 0.03,
            "output_usd_per_million_tokens": 2.5,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
        "gemini-2.5-flash-lite": {
            "input_usd_per_million_tokens": 0.1,
            "cached_input_usd_per_million_tokens": 0.01,
            "output_usd_per_million_tokens": 0.4,
            "output_includes_reasoning_tokens": True,
            "source": PRICING_SOURCES["Gemini"],
        },
    },
    "Moonshot": {
        "kimi-k2.6": {
            "input_usd_per_million_tokens": 0.95,
            "cached_input_usd_per_million_tokens": 0.16,
            "output_usd_per_million_tokens": 4.0,
            "source": PRICING_SOURCES["Moonshot"],
        },
        "kimi-k2.5": {
            "input_usd_per_million_tokens": 0.6,
            "cached_input_usd_per_million_tokens": 0.1,
            "output_usd_per_million_tokens": 3.0,
            "source": PRICING_SOURCES["Moonshot"],
        },
    },
}


def resolve_model_pricing(
    provider: Optional[str],
    model: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not provider or not model:
        return None

    provider_pricing = MODEL_PRICING.get(provider)
    if not provider_pricing:
        return None

    if model in provider_pricing:
        pricing = dict(provider_pricing[model])
        pricing["provider"] = provider
        pricing["model"] = model
        pricing["pricing_snapshot_id"] = PRICING_SNAPSHOT_ID
        return pricing

    for candidate, candidate_pricing in sorted(
        provider_pricing.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if model.startswith(f"{candidate}-"):
            pricing = dict(candidate_pricing)
            pricing["provider"] = provider
            pricing["model"] = model
            pricing["pricing_snapshot_id"] = PRICING_SNAPSHOT_ID
            return pricing

    return None


def estimate_usage_cost_usd(
    *,
    provider: Optional[str],
    model: Optional[str],
    usage: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if usage is None:
        return None

    pricing = resolve_model_pricing(provider, model)
    if pricing is None:
        return None

    input_tokens = int(usage.get("input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    reasoning_tokens = int(usage.get("reasoning_tokens") or 0)
    cached_input_tokens = min(int(usage.get("cached_input_tokens") or 0), input_tokens)
    uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)
    billable_output_tokens = output_tokens
    if pricing.get("output_includes_reasoning_tokens"):
        billable_output_tokens += reasoning_tokens

    input_rate = float(pricing["input_usd_per_million_tokens"])
    output_rate = float(pricing["output_usd_per_million_tokens"])
    cached_input_rate = pricing.get("cached_input_usd_per_million_tokens")
    if cached_input_rate is None:
        cached_input_rate = input_rate
    cached_input_rate = float(cached_input_rate)

    input_cost_usd = (uncached_input_tokens / 1_000_000) * input_rate
    cached_input_cost_usd = (cached_input_tokens / 1_000_000) * cached_input_rate
    output_cost_usd = (billable_output_tokens / 1_000_000) * output_rate
    total_cost_usd = input_cost_usd + cached_input_cost_usd + output_cost_usd

    return {
        "provider": provider,
        "model": model,
        "pricing_snapshot_id": pricing["pricing_snapshot_id"],
        "source": pricing["source"],
        "input_usd_per_million_tokens": input_rate,
        "cached_input_usd_per_million_tokens": cached_input_rate,
        "output_usd_per_million_tokens": output_rate,
        "input_cost_usd": round(input_cost_usd, 8),
        "cached_input_cost_usd": round(cached_input_cost_usd, 8),
        "output_cost_usd": round(output_cost_usd, 8),
        "total_cost_usd": round(total_cost_usd, 8),
    }
