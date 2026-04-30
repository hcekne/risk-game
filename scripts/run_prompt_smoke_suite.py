import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from risk_game.card_deck import Card
from risk_game.game_config import GameConfig
from risk_game.game_constants import TERRITORIES
from risk_game.game_master import GameMaster
from risk_game.game_state import GameState
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.llm_clients.llm_base import LLMClient
from risk_game.paths import get_game_results_subdir
from risk_game.player_agent import PlayerAgent
from risk_game.rules import Rules
from risk_game.utils.game_admin import (
    build_llm_interaction_logger,
    create_game_folder,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a fixed prompt/response smoke suite against live models and "
            "validate the outputs with the real Risk engine rules."
        )
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        required=True,
        help=(
            "Agent specs as Provider:Model, for example "
            "OpenAI:gpt-5.5 Gemini:gemini-3.1-pro-preview Moonshot:kimi-k2.6"
        ),
    )
    parser.add_argument(
        "--base-folder",
        default=str(get_game_results_subdir("prompt_smoke_runs")),
        help="Base folder for the smoke run artifacts.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional explicit output JSON path. Defaults inside the smoke run folder.",
    )
    return parser.parse_args()


class DummyLLMClient(LLMClient):
    def __init__(self) -> None:
        super().__init__(provider_name="dummy", model_type="dummy")

    def get_chat_completion(self, messages, **kwargs) -> str:
        raise RuntimeError("Dummy smoke-suite client should never be called.")


def set_territory_owner(
    game_state: GameState, territory: str, player_name: str, troops: int
) -> None:
    row_mask = game_state.territories_df["Territory"] == territory
    player_columns = list(game_state.territories_df.columns[1:])
    game_state.territories_df.loc[row_mask, player_columns] = 0
    game_state.territories_df.loc[row_mask, player_name] = troops


def build_smoke_game_master(candidate_player: PlayerAgent) -> GameMaster:
    config = GameConfig(
        progressive=True,
        capitals=False,
        max_rounds=15,
        turn_time_limit_seconds=90,
        placement_time_limit_seconds=15,
        placement_reasoning_effort="low",
        planning_reasoning_effort="medium",
        attack_reasoning_effort="medium",
        fortify_reasoning_effort="medium",
        card_trade_reasoning_effort="low",
    )
    rules = Rules(config)
    game_master = GameMaster(rules)
    opponent_one = PlayerAgent("Bob", DummyLLMClient())
    opponent_two = PlayerAgent("Carol", DummyLLMClient())
    game_master.players = [candidate_player, opponent_one, opponent_two]
    game_master.active_players = game_master.players.copy()
    game_master.dead_players = []
    game_master.player_cards = {player.name: [] for player in game_master.players}
    game_master.game_state = GameState(game_master.players, rules)
    game_master.deck = None
    game_master.phase = 0
    game_master.game_round = 1

    for player in game_master.players:
        game_master._apply_runtime_settings_to_player(player)

    setup_candidate_smoke_board(game_master.game_state, candidate_player.name)
    game_master.player_cards[candidate_player.name] = build_smoke_cards()
    return game_master


def setup_candidate_smoke_board(game_state: GameState, candidate_name: str) -> None:
    enemy_cycle = ["Bob", "Carol"]
    for index, territory in enumerate(TERRITORIES):
        set_territory_owner(game_state, territory, enemy_cycle[index % 2], 1)

    candidate_territories = {
        "Alaska": 4,
        "Northwest Territory": 3,
        "Alberta": 3,
        "Ontario": 2,
        "Greenland": 2,
        "Brazil": 2,
        "Argentina": 3,
        "Peru": 2,
    }
    for territory, troops in candidate_territories.items():
        set_territory_owner(game_state, territory, candidate_name, troops)

    enemy_adjustments = {
        "Kamchatka": ("Bob", 1),
        "Western United States": ("Carol", 1),
        "Eastern United States": ("Bob", 1),
        "Quebec": ("Carol", 1),
        "Venezuela": ("Bob", 1),
        "North Africa": ("Carol", 1),
    }
    for territory, (owner, troops) in enemy_adjustments.items():
        set_territory_owner(game_state, territory, owner, troops)


def build_smoke_cards() -> List[Card]:
    return [
        Card("Brazil", "infantry"),
        Card("Peru", "cavalry"),
        Card("Argentina", "canon"),
        Card("Greenland", "wild"),
    ]


def parse_agent_spec(spec: str) -> Tuple[str, str]:
    if ":" not in spec:
        raise ValueError(
            f"Invalid agent spec '{spec}'. Expected Provider:Model."
        )
    provider, model = spec.split(":", 1)
    return provider, model


def build_live_client(provider: str, model: str):
    if provider == "OpenAI":
        reasoning_effort = "none" if model.startswith("gpt-4.1") else "medium"
        return create_llm_client(
            provider,
            model,
            reasoning_effort=reasoning_effort,
            verbosity="low",
        )
    if provider == "Anthropic":
        return create_llm_client(
            provider,
            model,
            enable_thinking=False,
        )
    if provider == "Gemini":
        return create_llm_client(
            provider,
            model,
            reasoning_effort="medium",
        )
    if provider in {"Moonshot", "Kimi"}:
        return create_llm_client("Moonshot", model)
    raise ValueError(f"Unsupported provider for smoke suite: {provider}")


def decision_snapshot(player: PlayerAgent) -> Dict[str, Any]:
    latest = player.get_latest_turn_decision() or {}
    return {
        "interaction_index": latest.get("interaction_index"),
        "used_fallback_response": latest.get("used_fallback_response"),
        "error": latest.get("error"),
        "error_type": latest.get("error_type"),
        "timeout_seconds": latest.get("timeout_seconds"),
        "decision_time_seconds": latest.get("decision_time_seconds"),
        "reasoning_effort_override": latest.get("reasoning_effort_override"),
        "scope": latest.get("scope"),
    }


def run_pre_turn_planning(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.start_turn_timer(game_master.rules.turn_time_limit_seconds)
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_pre_turn_planning",
    )
    player.define_strategy_for_move(game_master.rules, game_master.game_state)
    player.clear_turn_timer()
    plan_text = player.turn_strategy.strip()
    word_count = len(plan_text.split())
    return {
        "phase": "pre_turn_planning",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {"plan_text": plan_text, "word_count": word_count},
        "valid": bool(plan_text) and word_count <= 60,
        "validation_error": None if plan_text and word_count <= 60 else "Plan empty or too long.",
        "decision": decision_snapshot(player),
    }


def run_initial_placement(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_initial_placement",
    )
    moves, reasoning, from_territory = player.make_initial_troop_placement(
        game_master.rules, game_master.game_state
    )
    is_valid, error = game_master.validate_move_phase_0(player, moves, reasoning)
    return {
        "phase": "initial_troop_placement",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "moves": moves,
            "reasoning": reasoning,
            "from_territory": from_territory,
        },
        "valid": is_valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_troop_placement(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.troops = 5
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_troop_placement",
    )
    moves, reasoning, from_territory = player.make_troop_placement(
        game_master.rules, game_master.game_state
    )
    is_valid, error = game_master.validate_move_phase_1(player, moves, reasoning)
    return {
        "phase": "troop_placement",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "moves": moves,
            "reasoning": reasoning,
            "from_territory": from_territory,
        },
        "valid": is_valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_attack(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.turn_strategy = "Take a clean adjacent territory if favorable."
    player.start_turn_timer(game_master.rules.turn_time_limit_seconds)
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_attack",
    )
    moves, reasoning, from_territory = player.make_attack_move(
        game_master.rules,
        game_master.game_state,
        successful_attacks=0,
    )
    player.clear_turn_timer()
    is_valid, error = game_master.validate_attack_move(
        player, moves, reasoning, from_territory
    )
    return {
        "phase": "attack",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "moves": moves,
            "reasoning": reasoning,
            "from_territory": from_territory,
        },
        "valid": is_valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_fortify(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.turn_strategy = "Pull reserves into the most exposed front."
    player.start_turn_timer(game_master.rules.turn_time_limit_seconds)
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_fortify",
    )
    moves, reasoning, from_territory = player.make_fortify_move(
        game_master.rules, game_master.game_state
    )
    player.clear_turn_timer()
    is_valid, error = game_master.validate_fortify_move(
        player, moves, reasoning, from_territory
    )
    return {
        "phase": "fortify",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "moves": moves,
            "reasoning": reasoning,
            "from_territory": from_territory,
        },
        "valid": is_valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_optional_card_trade(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.start_turn_timer(game_master.rules.turn_time_limit_seconds)
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_optional_card_trade",
    )
    cards = list(game_master.player_cards[player.name])
    valid_combinations = game_master.rules.find_valid_combinations(
        cards,
        player.name,
        game_master.game_state,
    )
    selected_cards, reasoning = player.may_trade_cards(
        cards,
        game_master.game_state,
        valid_combinations,
    )
    player.clear_turn_timer()

    valid = False
    error = None
    if selected_cards == [0]:
        valid = True
    elif selected_cards is None:
        error = "No card selection returned."
    else:
        try:
            proposed_cards = [cards[index - 1] for index in selected_cards]
            valid, _, _ = game_master.rules.verify_card_combination(
                proposed_cards,
                player.name,
                game_master.game_state,
            )
            if not valid:
                error = "Returned card set is not a valid trade."
        except Exception as exc:
            error = f"Failed to map selected cards: {exc}"

    return {
        "phase": "optional_card_trade",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "selected_cards": selected_cards,
            "reasoning": reasoning,
        },
        "valid": valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_mandatory_card_trade(
    game_master: GameMaster, player: PlayerAgent
) -> Dict[str, Any]:
    player.reset_turn_decision_log()
    player.start_turn_timer(game_master.rules.turn_time_limit_seconds)
    player.set_interaction_context(
        game_round=0,
        turn_number=None,
        scope="smoke_mandatory_card_trade",
    )
    cards = list(game_master.player_cards[player.name])
    valid_combinations = game_master.rules.find_valid_combinations(
        cards,
        player.name,
        game_master.game_state,
    )
    selected_cards, reasoning = player.must_trade_cards(
        cards,
        game_master.game_state,
        valid_combinations,
    )
    player.clear_turn_timer()

    valid = False
    error = None
    if selected_cards is None:
        error = "No card selection returned."
    else:
        try:
            proposed_cards = [cards[index - 1] for index in selected_cards]
            valid, _, _ = game_master.rules.verify_card_combination(
                proposed_cards,
                player.name,
                game_master.game_state,
            )
            if not valid:
                error = "Returned mandatory trade set is not valid."
        except Exception as exc:
            error = f"Failed to map selected cards: {exc}"

    return {
        "phase": "mandatory_card_trade",
        "raw_response": player.get_latest_turn_decision().get("raw_response"),
        "parsed": {
            "selected_cards": selected_cards,
            "reasoning": reasoning,
        },
        "valid": valid,
        "validation_error": error,
        "decision": decision_snapshot(player),
    }


def run_smoke_suite_for_agent(provider: str, model: str, game_folder: str) -> Dict[str, Any]:
    client = build_live_client(provider, model)
    player = PlayerAgent(f"{provider}_{model}", client)
    game_master = build_smoke_game_master(player)
    logger = build_llm_interaction_logger(game_folder)
    player.configure_llm_interaction_logger(logger)
    game_master.llm_interaction_logger = logger
    game_master._apply_runtime_settings_to_player(player)

    results = [
        run_pre_turn_planning(game_master, player),
        run_initial_placement(game_master, player),
        run_troop_placement(game_master, player),
        run_attack(game_master, player),
        run_fortify(game_master, player),
        run_optional_card_trade(game_master, player),
        run_mandatory_card_trade(game_master, player),
    ]
    return {
        "provider": provider,
        "model": model,
        "phases": results,
        "all_valid": all(result["valid"] for result in results),
        "fallback_count": sum(
            1 for result in results if result["decision"]["used_fallback_response"]
        ),
    }


def render_markdown_summary(results: List[Dict[str, Any]]) -> str:
    lines = ["# Prompt Smoke Summary", ""]
    for agent in results:
        lines.append(f"## {agent['provider']} · {agent['model']}")
        lines.append(
            f"- all_valid: {agent['all_valid']}\n"
            f"- fallback_count: {agent['fallback_count']}"
        )
        if agent.get("fatal_error"):
            lines.append(f"- fatal_error: {agent['fatal_error']}")
            lines.append("")
            continue
        for phase in agent["phases"]:
            decision = phase["decision"]
            lines.append(
                f"- {phase['phase']}: valid={phase['valid']} "
                f"time={decision['decision_time_seconds']}s "
                f"fallback={decision['used_fallback_response']}"
            )
            if phase["validation_error"]:
                lines.append(f"  error: {phase['validation_error']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    args = parse_args()
    game_folder = create_game_folder(base_folder=args.base_folder)

    results = []
    for spec in args.agents:
        provider, model = parse_agent_spec(spec)
        print(f"Running prompt smoke suite for {provider}:{model}")
        try:
            agent_result = run_smoke_suite_for_agent(provider, model, game_folder)
        except Exception as exc:
            agent_result = {
                "provider": provider,
                "model": model,
                "phases": [],
                "all_valid": False,
                "fallback_count": 0,
                "fatal_error": str(exc),
            }
        results.append(agent_result)
        print(
            f"  all_valid={agent_result['all_valid']} "
            f"fallbacks={agent_result['fallback_count']}"
        )

    output_path = (
        Path(args.output)
        if args.output is not None
        else Path(game_folder) / "prompt_smoke_results.json"
    )
    payload = {
        "game_folder": game_folder,
        "agents": args.agents,
        "shared_runtime_settings": GameConfig().to_dict(),
        "results": results,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    markdown_path = Path(game_folder) / "prompt_smoke_summary.md"
    markdown_path.write_text(render_markdown_summary(results))
    print(f"Saved smoke results to {output_path}")
    print(f"Saved smoke summary to {markdown_path}")


if __name__ == "__main__":
    main()
