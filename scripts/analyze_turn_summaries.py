import argparse
import json
from collections import defaultdict
from pathlib import Path

from risk_game.utils.strategic_rubric import score_turn_summary
from risk_game.utils.turn_summary import render_turn_summary_markdown


def load_turn_summaries(game_folder: Path) -> list[dict]:
    summary_files = sorted(
        game_folder.glob("turn_summary_turn_*.json"),
        key=lambda path: int(path.stem.split("_")[-1]),
    )
    return [json.loads(path.read_text()) for path in summary_files]


RUBRIC_DIMENSIONS = (
    "plan_concreteness",
    "action_validity",
    "plan_alignment",
    "tactical_efficiency",
    "positional_outcome",
)


def build_player_metrics(turn_summaries: list[dict]) -> dict[str, dict]:
    metrics: dict[str, dict] = defaultdict(
        lambda: {
            "turns": 0,
            "territory_delta_total": 0,
            "troop_delta_total": 0,
            "cards_delta_total": 0,
            "successful_attack_count": 0,
            "failed_attack_count": 0,
            "invalid_action_count": 0,
            "random_fallback_count": 0,
            "completed_card_trades": 0,
            "turn_time_total": 0.0,
            "continents_gained": [],
            "continents_lost": [],
            "rubric_total": 0.0,
            "rubric_dimensions_total": {dimension: 0.0 for dimension in RUBRIC_DIMENSIONS},
        }
    )

    for turn_summary in turn_summaries:
        player_name = turn_summary["player"]["name"]
        derived = turn_summary["derived"]
        rubric = turn_summary["rubric"]
        player_metrics = metrics[player_name]
        player_metrics["turns"] += 1
        player_metrics["territory_delta_total"] += derived["territory_delta"]
        player_metrics["troop_delta_total"] += derived["troop_delta"]
        player_metrics["cards_delta_total"] += derived["cards_delta"]
        player_metrics["successful_attack_count"] += derived["successful_attack_count"]
        player_metrics["failed_attack_count"] += derived["failed_attack_count"]
        player_metrics["invalid_action_count"] += derived["invalid_action_count"]
        player_metrics["random_fallback_count"] += derived["random_fallback_count"]
        player_metrics["completed_card_trades"] += derived["completed_card_trades"]
        player_metrics["turn_time_total"] += derived["turn_time_seconds"]
        player_metrics["continents_gained"].extend(derived["new_continents"])
        player_metrics["continents_lost"].extend(derived["lost_continents"])
        player_metrics["rubric_total"] += rubric["overall_score"]
        for dimension in RUBRIC_DIMENSIONS:
            player_metrics["rubric_dimensions_total"][dimension] += rubric["dimensions"][dimension]["score"]

    for player_metrics in metrics.values():
        turns = max(player_metrics["turns"], 1)
        player_metrics["avg_territory_delta"] = round(
            player_metrics["territory_delta_total"] / turns, 2
        )
        player_metrics["avg_troop_delta"] = round(
            player_metrics["troop_delta_total"] / turns, 2
        )
        player_metrics["avg_turn_time_seconds"] = round(
            player_metrics["turn_time_total"] / turns, 2
        )
        player_metrics["avg_rubric_score"] = round(
            player_metrics["rubric_total"] / turns, 2
        )
        player_metrics["avg_rubric_dimensions"] = {
            dimension: round(
                player_metrics["rubric_dimensions_total"][dimension] / turns,
                2,
            )
            for dimension in RUBRIC_DIMENSIONS
        }
        del player_metrics["rubric_total"]
        del player_metrics["rubric_dimensions_total"]

    return dict(metrics)


def build_turn_scorecards(turn_summaries: list[dict]) -> list[dict]:
    scorecards = []
    for turn_summary in turn_summaries:
        scorecards.append(
            {
                "turn_number": turn_summary["turn_number"],
                "game_round": turn_summary["game_round"],
                "player": turn_summary["player"]["name"],
                "rubric": turn_summary["rubric"],
                "derived": turn_summary["derived"],
                "plan": turn_summary["plan"]["text"],
            }
        )
    return scorecards


def build_markdown_report(
    game_folder: Path, end_game_results: dict | None, turn_summaries: list[dict]
) -> str:
    lines = [f"# Strategic Turn Analysis: {game_folder.name}", ""]

    if end_game_results is not None:
        lines.extend(
            [
                "## Game Overview",
                f"- Winner: {end_game_results['winner']}",
                f"- Victory condition: {end_game_results['victory_condition']}",
                f"- Total rounds: {end_game_results['total_rounds']}",
                "",
            ]
        )

    player_metrics = build_player_metrics(turn_summaries)
    lines.append("## Player Metrics")
    for player_name, metrics in sorted(player_metrics.items()):
        lines.append(
            (
                f"- {player_name}: turns={metrics['turns']}, "
                f"avg territory delta={metrics['avg_territory_delta']:+.2f}, "
                f"avg troop delta={metrics['avg_troop_delta']:+.2f}, "
                f"successful attacks={metrics['successful_attack_count']}, "
                f"failed attacks={metrics['failed_attack_count']}, "
                f"invalid actions={metrics['invalid_action_count']}, "
                f"card trades={metrics['completed_card_trades']}, "
                f"avg turn time={metrics['avg_turn_time_seconds']:.2f}s, "
                f"avg strategic score={metrics['avg_rubric_score']:.2f}/5"
            )
        )
        lines.append(
            (
                f"  rubric: plan={metrics['avg_rubric_dimensions']['plan_concreteness']:.2f}, "
                f"validity={metrics['avg_rubric_dimensions']['action_validity']:.2f}, "
                f"alignment={metrics['avg_rubric_dimensions']['plan_alignment']:.2f}, "
                f"tactics={metrics['avg_rubric_dimensions']['tactical_efficiency']:.2f}, "
                f"position={metrics['avg_rubric_dimensions']['positional_outcome']:.2f}"
            )
        )
    lines.extend(["", "## Turn By Turn"])

    for turn_summary in turn_summaries:
        lines.append(render_turn_summary_markdown(turn_summary))
        rubric = turn_summary["rubric"]
        lines.append(
            (
                f"Rubric: overall={rubric['overall_score']:.2f}/5 "
                f"({rubric['band']})"
            )
        )
        lines.append(rubric["summary"])
        for dimension, details in rubric["dimensions"].items():
            lines.append(
                f"- {dimension}: {details['score']}/5. "
                + " ".join(details["notes"])
            )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render saved turn summaries into a strategic analysis report."
    )
    parser.add_argument("--game-folder", required=True, help="Saved game folder.")
    parser.add_argument(
        "--output-dir",
        help="Optional output directory. Defaults to the game folder.",
    )
    args = parser.parse_args()

    game_folder = Path(args.game_folder)
    output_dir = Path(args.output_dir) if args.output_dir else game_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    turn_summaries = load_turn_summaries(game_folder)
    if not turn_summaries:
        raise ValueError(f"No turn summary files found in {game_folder}")
    for turn_summary in turn_summaries:
        turn_summary["rubric"] = score_turn_summary(turn_summary)

    end_game_path = game_folder / "end_game_results.json"
    end_game_results = None
    if end_game_path.exists():
        end_game_results = json.loads(end_game_path.read_text())

    player_metrics = build_player_metrics(turn_summaries)
    metrics_path = output_dir / "strategic_metrics.json"
    metrics_path.write_text(json.dumps(player_metrics, indent=2))

    turn_scorecards_path = output_dir / "strategic_turn_scores.json"
    turn_scorecards_path.write_text(
        json.dumps(build_turn_scorecards(turn_summaries), indent=2)
    )

    report_path = output_dir / "strategic_analysis.md"
    report_path.write_text(
        build_markdown_report(game_folder, end_game_results, turn_summaries)
    )

    print(
        json.dumps(
            {
                "game_folder": str(game_folder),
                "report_path": str(report_path),
                "metrics_path": str(metrics_path),
                "turn_scorecards_path": str(turn_scorecards_path),
                "turn_count": len(turn_summaries),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
