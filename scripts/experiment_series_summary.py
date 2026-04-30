import argparse
import json
from pathlib import Path

from risk_game.paths import get_game_results_subdir
from risk_game.utils.experiment_batch import (
    build_series_manifest,
    combine_experiment_results,
    compute_experiment_summary,
    load_experiment_context,
    render_experiment_summary_markdown,
    save_json,
    sanitize_path_component,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Combine multiple compatible experiment folders into one staged "
            "series summary."
        )
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Combined series label.",
    )
    parser.add_argument(
        "--experiment-folders",
        nargs="+",
        required=True,
        help="Experiment folders to combine, in chronological order.",
    )
    parser.add_argument(
        "--base-folder",
        default=str(get_game_results_subdir("experiment_series")),
        help="Base directory for combined series outputs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the combined JSON summary instead of markdown.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contexts = [load_experiment_context(folder) for folder in args.experiment_folders]
    combined_manifest = build_series_manifest(
        label=args.label,
        contexts=contexts,
    )
    combined_results = combine_experiment_results(contexts)
    combined_summary = compute_experiment_summary(combined_manifest, combined_results)

    output_folder = (
        Path(args.base_folder) / sanitize_path_component(args.label)
    )
    output_folder.mkdir(parents=True, exist_ok=True)

    save_json(output_folder / "series_manifest.json", combined_manifest)
    save_json(output_folder / "series_results.json", {"results": combined_results})
    save_json(output_folder / "series_summary.json", combined_summary)

    markdown = render_experiment_summary_markdown(
        combined_manifest,
        combined_summary,
    )
    (output_folder / "series_summary.md").write_text(markdown)

    if args.json:
        print(json.dumps(combined_summary, indent=2))
        return
    print(markdown, end="")


if __name__ == "__main__":
    main()
