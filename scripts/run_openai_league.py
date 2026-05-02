import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from risk_game.experiments import AgentSpec, Experiment
from risk_game.game_config import GameConfig
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.paths import get_game_results_dir


REASONING_ORDER = ["none", "low", "medium", "high", "xhigh"]


def cap_reasoning_effort(
    requested_effort: str,
    max_effort: str,
) -> str:
    if requested_effort not in REASONING_ORDER:
        raise ValueError(
            f"Unknown requested reasoning effort '{requested_effort}'. "
            f"Choose from {REASONING_ORDER}."
        )
    if max_effort not in REASONING_ORDER:
        raise ValueError(
            f"Unknown max reasoning effort '{max_effort}'. "
            f"Choose from {REASONING_ORDER}."
        )

    requested_index = REASONING_ORDER.index(requested_effort)
    max_index = REASONING_ORDER.index(max_effort)
    return REASONING_ORDER[min(requested_index, max_index)]


def resolve_phase_reasoning_effort(
    requested_effort: str,
    explicit_effort: Optional[str],
    max_effort: str,
) -> str:
    if explicit_effort is not None:
        return explicit_effort
    return cap_reasoning_effort(requested_effort, max_effort)


def run_openai_preflight(agent_specs: list[AgentSpec]) -> None:
    print("Running OpenAI preflight checks...")
    checked_models = set()
    for spec in agent_specs:
        model_name = str(spec.model)
        reasoning_effort = spec.reasoning_effort
        model_key = (model_name, reasoning_effort)
        if model_key in checked_models:
            continue
        checked_models.add(model_key)
        client = create_llm_client(
            "OpenAI",
            model_name,
            use_responses_api=spec.use_responses_api,
            reasoning_effort=reasoning_effort,
            verbosity=spec.verbosity,
        )
        try:
            response = client.get_chat_completion(
                "Reply with exactly OK.",
                reasoning_effort=reasoning_effort,
                timeout_seconds=30,
                max_attempts_override=1,
            )
        except Exception as exc:
            raise RuntimeError(
                f"OpenAI preflight failed for model '{model_name}' "
                f"with reasoning_effort='{reasoning_effort}': {exc}"
            ) from exc

        print(
            f"Preflight OK for {model_name} ({reasoning_effort}): "
            f"{response.strip()[:60] or '[empty]'}"
        )


def build_summary(game, game_index: int, game_folder: str, elapsed_seconds: float) -> dict:
    territories = {
        player.name: len(game.game_state.get_player_territories(player.name))
        for player in game.players
    }
    turn_times = {
        player.name: round(player.accumulated_turn_time, 2)
        for player in game.players
    }
    error_counts = {
        player.name: {
            "placement": player.troop_placement_errors,
            "attack": player.attack_errors,
            "fortify": player.fortify_errors,
            "card_trade": player.card_trade_errors,
            "formatting": player.return_formatting_errors,
        }
        for player in game.players
    }
    strategic_scores = {}
    llm_fallback_counts = {}
    for player_name in territories:
        player_turns = [
            turn_summary
            for turn_summary in game.turn_summaries
            if turn_summary["player"]["name"] == player_name
        ]
        if not player_turns:
            continue
        average_score = sum(
            turn_summary["rubric"]["overall_score"]
            for turn_summary in player_turns
            if "rubric" in turn_summary
        ) / len(player_turns)
        strategic_scores[player_name] = round(average_score, 2)
        llm_fallback_counts[player_name] = sum(
            1
            for turn_summary in player_turns
            for decision in turn_summary.get("llm_decisions", [])
            if decision.get("used_fallback_response")
        )

    return {
        "game": game_index,
        "config": {
            "progressive": game.rules.progressive,
            "capitals": game.rules.capitals,
            "territory_control_percentage": game.rules.territory_control_percentage,
            "required_continents": game.rules.required_continents,
            "key_areas": game.rules.key_areas,
            "max_rounds": game.rules.max_rounds,
            "turn_time_limit_seconds": game.rules.turn_time_limit_seconds,
            "planning_time_limit_seconds": game.rules.planning_time_limit_seconds,
            "placement_time_limit_seconds": game.rules.placement_time_limit_seconds,
            "placement_reasoning_effort": game.rules.placement_reasoning_effort,
            "planning_reasoning_effort": game.rules.planning_reasoning_effort,
            "attack_reasoning_effort": game.rules.attack_reasoning_effort,
            "fortify_reasoning_effort": game.rules.fortify_reasoning_effort,
            "card_trade_reasoning_effort": game.rules.card_trade_reasoning_effort,
        },
        "winner": game.winner.name if game.winner else None,
        "victory_condition": game.victory_condition,
        "rounds": game.game_round,
        "elapsed_seconds": round(elapsed_seconds, 2),
        "territories": territories,
        "turn_times": turn_times,
        "error_counts": error_counts,
        "strategic_scores": strategic_scores,
        "llm_fallback_counts": llm_fallback_counts,
        "game_folder": game_folder,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an OpenAI-only Risk league and save an aggregate summary.")
    parser.add_argument("--label", required=True, help="Summary label prefix.")
    parser.add_argument("--num-games", type=int, default=10, help="Number of games.")
    parser.add_argument(
        "--reasoning-effort",
        default="medium",
        help="Reasoning effort to use for every model.",
    )
    parser.add_argument(
        "--verbosity",
        default="low",
        help="Responses API text verbosity.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=15,
        help="Maximum rounds per game.",
    )
    parser.add_argument(
        "--base-folder",
        default=str(get_game_results_dir()),
        help="Directory where game folders and the final summary file will be written.",
    )
    parser.add_argument(
        "--turn-time-limit-seconds",
        type=int,
        default=90,
        help="Hard per-turn wall-clock budget. If it expires, the turn is effectively forfeited.",
    )
    parser.add_argument(
        "--planning-time-limit-seconds",
        type=int,
        default=None,
        help=(
            "Optional isolated wall-clock budget for the single pre-turn planning "
            "prompt. This runs before the shared execution turn timer starts."
        ),
    )
    parser.add_argument(
        "--placement-time-limit-seconds",
        type=int,
        default=15,
        help="Hard per-call wall-clock budget for initial placement and troop placement prompts.",
    )
    parser.add_argument(
        "--placement-reasoning-effort",
        default="low",
        help="Reasoning effort used only for placement prompts.",
    )
    parser.add_argument(
        "--planning-reasoning-effort",
        default=None,
        help="Reasoning effort for pre-turn planning prompts. Defaults to the global effort capped at medium.",
    )
    parser.add_argument(
        "--attack-reasoning-effort",
        default=None,
        help="Reasoning effort for attack prompts. Defaults to the global effort capped at medium.",
    )
    parser.add_argument(
        "--fortify-reasoning-effort",
        default=None,
        help="Reasoning effort for fortify prompts. Defaults to the global effort capped at medium.",
    )
    parser.add_argument(
        "--card-trade-reasoning-effort",
        default=None,
        help="Reasoning effort for card-trade prompts. Defaults to the global effort capped at low.",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip the live OpenAI preflight request check before starting the league.",
    )
    args = parser.parse_args()

    planning_reasoning_effort = resolve_phase_reasoning_effort(
        args.reasoning_effort,
        args.planning_reasoning_effort,
        "medium",
    )
    attack_reasoning_effort = resolve_phase_reasoning_effort(
        args.reasoning_effort,
        args.attack_reasoning_effort,
        "medium",
    )
    fortify_reasoning_effort = resolve_phase_reasoning_effort(
        args.reasoning_effort,
        args.fortify_reasoning_effort,
        "medium",
    )
    card_trade_reasoning_effort = resolve_phase_reasoning_effort(
        args.reasoning_effort,
        args.card_trade_reasoning_effort,
        "low",
    )

    config = GameConfig(
        progressive=True,
        capitals=False,
        max_rounds=args.max_rounds,
        turn_time_limit_seconds=args.turn_time_limit_seconds,
        planning_time_limit_seconds=args.planning_time_limit_seconds,
        placement_time_limit_seconds=args.placement_time_limit_seconds,
        placement_reasoning_effort=args.placement_reasoning_effort,
        planning_reasoning_effort=planning_reasoning_effort,
        attack_reasoning_effort=attack_reasoning_effort,
        fortify_reasoning_effort=fortify_reasoning_effort,
        card_trade_reasoning_effort=card_trade_reasoning_effort,
    )
    agent_specs = [
        AgentSpec(
            name="gpt-5.4",
            provider="OpenAI",
            model="gpt-5.4",
            reasoning_effort=args.reasoning_effort,
            verbosity=args.verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-mini",
            provider="OpenAI",
            model="gpt-5.4-mini",
            reasoning_effort=args.reasoning_effort,
            verbosity=args.verbosity,
        ),
        AgentSpec(
            name="gpt-5.4-nano",
            provider="OpenAI",
            model="gpt-5.4-nano",
            reasoning_effort=args.reasoning_effort,
            verbosity=args.verbosity,
        ),
    ]

    if not args.skip_preflight:
        run_openai_preflight(agent_specs)

    experiment = Experiment(
        config,
        num_games=args.num_games,
        agent_specs=agent_specs,
    )
    print(experiment)

    all_results = []
    for game_index in range(1, args.num_games + 1):
        print(f"Starting game {game_index}/{args.num_games}...")
        game = experiment.initialize_game()
        start_time = time.time()
        game_folder = game.play_game(
            include_initial_troop_placement=True,
            base_folder=args.base_folder,
        )
        elapsed_seconds = time.time() - start_time
        for turn_summary in game.turn_summaries:
            from risk_game.utils.strategic_rubric import score_turn_summary

            turn_summary["rubric"] = score_turn_summary(turn_summary)
        result = build_summary(game, game_index, game_folder, elapsed_seconds)
        all_results.append(result)
        print(json.dumps(result, indent=2))

    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_path = Path(args.base_folder) / f"{args.label}_{timestamp}.json"
    output_path.write_text(json.dumps(all_results, indent=2))
    print(f"Saved league summary to {output_path}")


if __name__ == "__main__":
    main()
