import argparse
import json

from risk_game.paths import get_game_results_subdir
from risk_game.utils.experiment_batch import (
    compute_experiment_summary,
    find_latest_experiment_folder,
    load_experiment_context,
    render_experiment_summary_markdown,
    save_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recompute and print the summary for an experiment batch."
    )
    parser.add_argument(
        "--experiment-folder",
        help="Explicit experiment folder. Defaults to the latest under --base-folder.",
    )
    parser.add_argument(
        "--base-folder",
        default=str(get_game_results_subdir("experiments")),
        help="Base directory searched when --experiment-folder is omitted.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the computed JSON summary instead of markdown.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiment_folder = (
        args.experiment_folder
        if args.experiment_folder
        else str(find_latest_experiment_folder(args.base_folder))
    )
    context = load_experiment_context(experiment_folder)
    summary = compute_experiment_summary(context["manifest"], context["results"])

    save_json(
        context["experiment_folder"] / "experiment_summary.json",
        summary,
    )
    markdown = render_experiment_summary_markdown(
        context["manifest"],
        summary,
    )
    (context["experiment_folder"] / "experiment_summary.md").write_text(markdown)

    if args.json:
        print(json.dumps(summary, indent=2))
        return
    print(markdown, end="")


if __name__ == "__main__":
    main()
