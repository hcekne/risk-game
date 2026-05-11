import argparse
import traceback
from pathlib import Path
from time import time
from typing import List

from risk_game.experiments import (
    AgentSpec,
    Experiment,
    build_live_turn_frontier_roster,
    build_live_turn_frontier_strategic_roster,
    build_openai_generation_ladder,
    build_openai_mini_high_strategic_hybrid_arena,
    build_openai_mini_medium_vs_high_arena,
    build_openai_mini_reasoning_arena,
    build_openai_nano_reasoning_arena,
    build_openai_size_ladder,
)
from risk_game.game_config import GameConfig
from risk_game.paths import get_game_results_subdir
from risk_game.utils.experiment_batch import (
    build_experiment_manifest,
    build_experiment_status,
    build_game_result,
    compute_experiment_summary,
    create_experiment_folder,
    load_agent_specs,
    render_experiment_summary_markdown,
    resolve_phase_reasoning_effort,
    rotate_agent_specs,
    run_agent_preflight,
    save_json,
    write_experiment_manifest,
    write_experiment_results,
    write_experiment_status,
)
from risk_game.utils.provider_pause import ExperimentPauseController


PRESET_NAMES = [
    "openai_generation_ladder",
    "openai_size_ladder",
    "openai_mini_reasoning",
    "openai_mini_medium_vs_high",
    "openai_mini_high_strategic_hybrid",
    "openai_nano_reasoning",
    "live_turn_frontier",
    "live_turn_frontier_strategic",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a scored Risk experiment batch, write structured status/results "
            "artifacts, and avoid expensive interactive monitoring."
        )
    )
    parser.add_argument("--label", required=True, help="Experiment label.")
    parser.add_argument(
        "--preset",
        choices=PRESET_NAMES,
        help="Named agent roster preset.",
    )
    parser.add_argument(
        "--agent-specs-file",
        help="Optional JSON file containing an explicit list of AgentSpec-like objects.",
    )
    parser.add_argument("--num-games", type=int, default=1, help="Number of games.")
    parser.add_argument(
        "--base-folder",
        default=str(get_game_results_subdir("experiments")),
        help="Base directory for experiment folders.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=15,
        help="Maximum rounds per game.",
    )
    parser.add_argument(
        "--turn-time-limit-seconds",
        type=int,
        default=None,
        help="Per-turn wall-clock budget.",
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
        default=None,
        help="Per-call wall-clock budget for placement prompts.",
    )
    parser.add_argument(
        "--placement-reasoning-effort",
        default=None,
        help="Reasoning effort used only for placement prompts.",
    )
    parser.add_argument(
        "--reasoning-effort",
        default="medium",
        help=(
            "Global requested reasoning effort for applicable preset builders. "
            "Phase-specific settings are still capped for live play."
        ),
    )
    parser.add_argument(
        "--verbosity",
        default="low",
        help="OpenAI Responses API verbosity for applicable presets.",
    )
    parser.add_argument(
        "--planning-reasoning-effort",
        default=None,
        help="Override planning reasoning effort.",
    )
    parser.add_argument(
        "--attack-reasoning-effort",
        default=None,
        help="Override attack reasoning effort.",
    )
    parser.add_argument(
        "--fortify-reasoning-effort",
        default=None,
        help="Override fortify reasoning effort.",
    )
    parser.add_argument(
        "--card-trade-reasoning-effort",
        default=None,
        help="Override card-trade reasoning effort.",
    )
    parser.add_argument(
        "--disable-seat-rotation",
        action="store_true",
        help="Disable cyclic seat rotation between games.",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip the live provider preflight requests before the batch starts.",
    )
    return parser.parse_args()


def build_agent_specs(args: argparse.Namespace) -> List[AgentSpec]:
    if args.agent_specs_file:
        return load_agent_specs(args.agent_specs_file)

    if args.preset == "openai_generation_ladder":
        return build_openai_generation_ladder(verbosity=args.verbosity)
    if args.preset == "openai_size_ladder":
        return build_openai_size_ladder(
            reasoning_effort=args.reasoning_effort,
            verbosity=args.verbosity,
        )
    if args.preset == "openai_mini_reasoning":
        return build_openai_mini_reasoning_arena(verbosity=args.verbosity)
    if args.preset == "openai_mini_medium_vs_high":
        return build_openai_mini_medium_vs_high_arena(verbosity=args.verbosity)
    if args.preset == "openai_mini_high_strategic_hybrid":
        return build_openai_mini_high_strategic_hybrid_arena(verbosity=args.verbosity)
    if args.preset == "openai_nano_reasoning":
        return build_openai_nano_reasoning_arena(verbosity=args.verbosity)
    if args.preset == "live_turn_frontier":
        return build_live_turn_frontier_roster()
    if args.preset == "live_turn_frontier_strategic":
        return build_live_turn_frontier_strategic_roster()

    raise ValueError("Either --preset or --agent-specs-file must be provided.")


def build_config(args: argparse.Namespace) -> GameConfig:
    default_turn_time_limit_seconds = 90
    default_planning_time_limit_seconds = None
    default_placement_time_limit_seconds = 15
    default_placement_reasoning_effort = "low"
    if args.preset == "openai_mini_reasoning":
        default_turn_time_limit_seconds = 120
        default_placement_time_limit_seconds = 25
    if args.preset == "openai_mini_medium_vs_high":
        default_turn_time_limit_seconds = 300
        default_placement_time_limit_seconds = 50
    if args.preset == "openai_mini_high_strategic_hybrid":
        default_turn_time_limit_seconds = 300
        default_placement_time_limit_seconds = 25
    if args.preset == "live_turn_frontier_strategic":
        default_planning_time_limit_seconds = 90
        default_placement_reasoning_effort = "medium"

    turn_time_limit_seconds = (
        default_turn_time_limit_seconds
        if args.turn_time_limit_seconds is None
        else args.turn_time_limit_seconds
    )
    planning_time_limit_seconds = (
        default_planning_time_limit_seconds
        if args.planning_time_limit_seconds is None
        else args.planning_time_limit_seconds
    )
    placement_time_limit_seconds = (
        default_placement_time_limit_seconds
        if args.placement_time_limit_seconds is None
        else args.placement_time_limit_seconds
    )
    placement_reasoning_effort = (
        default_placement_reasoning_effort
        if args.placement_reasoning_effort is None
        else args.placement_reasoning_effort
    )

    if args.preset == "live_turn_frontier_strategic" and args.planning_reasoning_effort is None:
        planning_reasoning_effort = "high"
    else:
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

    return GameConfig(
        progressive=True,
        capitals=False,
        max_rounds=args.max_rounds,
        turn_time_limit_seconds=turn_time_limit_seconds,
        planning_time_limit_seconds=planning_time_limit_seconds,
        placement_time_limit_seconds=placement_time_limit_seconds,
        placement_reasoning_effort=placement_reasoning_effort,
        planning_reasoning_effort=planning_reasoning_effort,
        attack_reasoning_effort=attack_reasoning_effort,
        fortify_reasoning_effort=fortify_reasoning_effort,
        card_trade_reasoning_effort=card_trade_reasoning_effort,
    )


def write_experiment_summary_artifacts(
    experiment_folder: Path,
    manifest: dict,
    results: List[dict],
) -> None:
    summary = compute_experiment_summary(manifest, results)
    save_json(experiment_folder / "experiment_summary.json", summary)
    (experiment_folder / "experiment_summary.md").write_text(
        render_experiment_summary_markdown(manifest, summary)
    )


def main() -> None:
    args = parse_args()
    agent_specs = build_agent_specs(args)
    config = build_config(args)
    experiment_folder = create_experiment_folder(
        label=args.label,
        base_folder=args.base_folder,
    )
    print(f"Experiment folder: {experiment_folder}")

    manifest = build_experiment_manifest(
        label=args.label,
        preset_name=args.preset,
        num_games=args.num_games,
        config=config,
        agent_specs=agent_specs,
        seat_rotation_enabled=not args.disable_seat_rotation,
        base_folder=args.base_folder,
    )
    write_experiment_manifest(experiment_folder, manifest)
    pause_controller = ExperimentPauseController(
        experiment_folder=experiment_folder,
        manifest=manifest,
    )

    results: List[dict] = []
    status = build_experiment_status(
        manifest=manifest,
        state="pending",
        experiment_folder=experiment_folder,
        completed_games=0,
    )
    write_experiment_status(experiment_folder, status)

    def pause_for_provider_issue(
        details: dict,
        *,
        current_game_index: int | None,
        current_seat_order: List[str] | None,
    ) -> None:
        pause_controller.pause_for_provider_issue(
            signal=details["signal"],
            provider=details["provider"],
            model=details["model"],
            player_name=details["player_name"],
            phase=details["phase"],
            client_role=details["client_role"],
            scope=details["scope"],
            completed_games=len(results),
            current_game_index=current_game_index,
            current_seat_order=current_seat_order,
            last_completed_game_folder=results[-1]["game_folder"] if results else None,
            last_winner=results[-1]["winner"] if results else None,
        )

    try:
        if not args.skip_preflight:
            print("Running provider preflight checks...")
            preflight_results = run_agent_preflight(
                agent_specs,
                pause_handler=lambda details: pause_for_provider_issue(
                    details,
                    current_game_index=None,
                    current_seat_order=None,
                ),
            )
            save_json(
                experiment_folder / "preflight_results.json",
                {"results": preflight_results},
            )

        status = build_experiment_status(
            manifest=manifest,
            state="running",
            experiment_folder=experiment_folder,
            completed_games=0,
        )
        write_experiment_status(experiment_folder, status)

        for game_index in range(1, args.num_games + 1):
            seat_specs = (
                rotate_agent_specs(agent_specs, game_index)
                if not args.disable_seat_rotation
                else list(agent_specs)
            )
            seat_order = [spec.name for spec in seat_specs]
            print(
                f"Starting game {game_index}/{args.num_games} "
                f"with seat order: {seat_order}"
            )
            status = build_experiment_status(
                manifest=manifest,
                state="running",
                experiment_folder=experiment_folder,
                completed_games=len(results),
                current_game_index=game_index,
                current_seat_order=seat_order,
                last_completed_game_folder=results[-1]["game_folder"] if results else None,
                last_winner=results[-1]["winner"] if results else None,
            )
            write_experiment_status(experiment_folder, status)

            experiment = Experiment(config, num_games=1, agent_specs=seat_specs)
            game = experiment.initialize_game()
            for player in game.players:
                if hasattr(player, "configure_provider_pause_handler"):
                    player.configure_provider_pause_handler(
                        lambda details, game_index=game_index, order=seat_order: (
                            pause_for_provider_issue(
                                details,
                                current_game_index=game_index,
                                current_seat_order=order,
                            )
                        )
                    )
            started_at = time()
            game_folder = game.play_game(
                include_initial_troop_placement=True,
                base_folder=str(experiment_folder),
            )
            elapsed_seconds = time() - started_at
            result = build_game_result(
                game,
                game_index=game_index,
                game_folder=game_folder,
                elapsed_seconds=elapsed_seconds,
                seat_order=seat_order,
            )
            results.append(result)
            write_experiment_results(experiment_folder, results)
            write_experiment_summary_artifacts(experiment_folder, manifest, results)

            status = build_experiment_status(
                manifest=manifest,
                state="running",
                experiment_folder=experiment_folder,
                completed_games=len(results),
                last_completed_game_folder=game_folder,
                last_winner=result["winner"],
            )
            write_experiment_status(experiment_folder, status)

        status = build_experiment_status(
            manifest=manifest,
            state="completed",
            experiment_folder=experiment_folder,
            completed_games=len(results),
            last_completed_game_folder=results[-1]["game_folder"] if results else None,
            last_winner=results[-1]["winner"] if results else None,
        )
        write_experiment_status(experiment_folder, status)
        write_experiment_summary_artifacts(experiment_folder, manifest, results)
        print(
            f"Experiment completed: {len(results)}/{args.num_games} games. "
            f"Summary written to {experiment_folder / 'experiment_summary.json'}"
        )
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        save_json(
            experiment_folder / "experiment_failure.json",
            {
                "error": error_message,
                "traceback": traceback.format_exc(),
            },
        )
        status = build_experiment_status(
            manifest=manifest,
            state="failed",
            experiment_folder=experiment_folder,
            completed_games=len(results),
            current_game_index=len(results) + 1 if len(results) < args.num_games else None,
            error=error_message,
            last_completed_game_folder=results[-1]["game_folder"] if results else None,
            last_winner=results[-1]["winner"] if results else None,
        )
        write_experiment_status(experiment_folder, status)
        write_experiment_results(experiment_folder, results)
        write_experiment_summary_artifacts(experiment_folder, manifest, results)
        raise


if __name__ == "__main__":
    main()
