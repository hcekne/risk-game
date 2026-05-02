import pytest

from risk_game.experiments import (
    build_live_turn_frontier_roster,
    build_live_turn_frontier_strategic_roster,
    build_openai_generation_ladder,
    build_openai_mini_high_strategic_hybrid_arena,
    build_openai_mini_medium_vs_high_arena,
    build_openai_mini_reasoning_arena,
    build_openai_size_ladder,
)


pytestmark = pytest.mark.regression


def test_build_live_turn_frontier_roster_uses_locked_defaults():
    roster = build_live_turn_frontier_roster()

    assert [agent.provider for agent in roster] == [
        "OpenAI",
        "Anthropic",
        "Gemini",
        "Moonshot",
    ]
    assert [agent.model for agent in roster] == [
        "gpt-5.5",
        "claude-opus-4-7",
        "gemini-3.1-pro-preview",
        "kimi-k2.6",
    ]

    assert roster[0].reasoning_effort == "medium"
    assert roster[0].verbosity == "low"

    assert roster[1].enable_thinking is False
    assert roster[1].thinking_effort is None

    assert roster[2].reasoning_effort == "medium"

    assert roster[3].enable_thinking is False


def test_build_live_turn_frontier_roster_allows_explicit_overrides():
    roster = build_live_turn_frontier_roster(
        openai_model="gpt-5.4",
        openai_reasoning_effort="high",
        anthropic_enable_thinking=True,
        anthropic_thinking_effort="medium",
    )

    assert roster[0].model == "gpt-5.4"
    assert roster[0].reasoning_effort == "high"
    assert roster[1].enable_thinking is True
    assert roster[1].thinking_effort == "medium"


def test_build_live_turn_frontier_strategic_roster_uses_high_planning_profile():
    roster = build_live_turn_frontier_strategic_roster()

    assert [agent.provider for agent in roster] == [
        "OpenAI",
        "Anthropic",
        "Gemini",
        "Moonshot",
    ]
    assert [agent.model for agent in roster] == [
        "gpt-5.4",
        "claude-opus-4-7",
        "gemini-3.1-pro-preview",
        "kimi-k2.6",
    ]
    assert roster[0].planning_provider == "OpenAI"
    assert roster[0].planning_model == "gpt-5.5"
    assert [agent.planning_time_limit_seconds for agent in roster] == [90, 90, 90, 90]
    assert [agent.placement_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "medium",
        "medium",
    ]
    assert [agent.planning_reasoning_effort for agent in roster] == [
        "high",
        "high",
        "high",
        "high",
    ]
    assert [agent.attack_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "medium",
        "medium",
    ]
    assert roster[1].enable_thinking is True
    assert roster[2].enable_thinking is True
    assert roster[3].enable_thinking is False
    assert roster[3].planning_provider == "Moonshot"
    assert roster[3].planning_model == "kimi-k2.6"
    assert roster[3].planning_enable_thinking is True


def test_build_openai_generation_ladder_uses_expected_models():
    roster = build_openai_generation_ladder()

    assert [agent.model for agent in roster] == [
        "gpt-5.5",
        "gpt-5.4",
        "gpt-4.1",
    ]
    assert [agent.reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "none",
    ]


def test_build_openai_size_ladder_uses_expected_models():
    roster = build_openai_size_ladder(reasoning_effort="high")

    assert [agent.model for agent in roster] == [
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-5.4-nano",
    ]
    assert [agent.reasoning_effort for agent in roster] == [
        "high",
        "high",
        "high",
    ]


def test_build_openai_mini_reasoning_arena_uses_phase_specific_reasoning_levels():
    roster = build_openai_mini_reasoning_arena()

    assert [agent.model for agent in roster] == [
        "gpt-5.4-mini",
        "gpt-5.4-mini",
        "gpt-5.4-mini",
        "gpt-5.4-mini",
    ]
    assert [agent.reasoning_effort for agent in roster] == [
        "none",
        "low",
        "medium",
        "high",
    ]
    assert [agent.attack_reasoning_effort for agent in roster] == [
        "none",
        "low",
        "medium",
        "high",
    ]
    assert [agent.placement_reasoning_effort for agent in roster] == [
        "none",
        "low",
        "medium",
        "high",
    ]
    assert [agent.card_trade_reasoning_effort for agent in roster] == [
        "none",
        "low",
        "medium",
        "high",
    ]


def test_build_openai_mini_medium_vs_high_arena_uses_balanced_two_vs_two_profiles():
    roster = build_openai_mini_medium_vs_high_arena()

    assert [agent.name for agent in roster] == [
        "gpt-5.4-mini-medium-a",
        "gpt-5.4-mini-medium-b",
        "gpt-5.4-mini-high-a",
        "gpt-5.4-mini-high-b",
    ]
    assert [agent.reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert [agent.placement_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert [agent.attack_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]


def test_build_openai_mini_high_strategic_hybrid_arena_uses_phase_split_profiles():
    roster = build_openai_mini_high_strategic_hybrid_arena()

    assert [agent.name for agent in roster] == [
        "gpt-5.4-mini-medium-all-a",
        "gpt-5.4-mini-medium-all-b",
        "gpt-5.4-mini-high-strategic-a",
        "gpt-5.4-mini-high-strategic-b",
    ]
    assert [agent.reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert [agent.placement_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "medium",
        "medium",
    ]
    assert [agent.planning_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert [agent.attack_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert [agent.fortify_reasoning_effort for agent in roster] == [
        "medium",
        "medium",
        "medium",
        "medium",
    ]
