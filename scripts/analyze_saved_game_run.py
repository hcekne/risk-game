import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from risk_game.game_constants import CONTINENT_BONUSES


def load_turn_metrics(game_folder: Path) -> pd.DataFrame:
    records = []
    state_files = sorted(
        game_folder.glob("game_state_turn_*.csv"),
        key=lambda path: int(path.stem.split("_")[-1]),
    )

    for state_path in state_files:
        df = pd.read_csv(state_path)
        turn_number = int(state_path.stem.split("_")[-1])
        game_round = int(df["Game_Round"].iloc[0])
        player_columns = [
            column
            for column in df.columns
            if column not in ("Territory", "Turn_Number", "Game_Round")
        ]

        for player in player_columns:
            territories = int((df[player] > 0).sum())
            troops = int(df[player].sum())
            controlled = set(df.loc[df[player] > 0, "Territory"])
            continents = [
                continent
                for continent, (continent_territories, _) in CONTINENT_BONUSES.items()
                if set(continent_territories).issubset(controlled)
            ]
            bonus = sum(CONTINENT_BONUSES[continent][1] for continent in continents)

            records.append(
                {
                    "turn": turn_number,
                    "round": game_round,
                    "player": player,
                    "territories": territories,
                    "troops": troops,
                    "continents": ",".join(continents),
                    "continent_bonus": bonus,
                }
            )

    return pd.DataFrame(records)


def make_game_plot(turn_metrics: pd.DataFrame, winner: str, output_path: Path, title: str) -> None:
    colors = {
        winner: "#d62728",
    }
    fallback_colors = ["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]

    fig, ax = plt.subplots(figsize=(11, 6))
    players = list(turn_metrics["player"].unique())
    color_index = 0

    for player in players:
        player_df = turn_metrics[turn_metrics["player"] == player].sort_values("turn")
        color = colors.get(player)
        if color is None:
            color = fallback_colors[color_index % len(fallback_colors)]
            color_index += 1

        line_width = 3.0 if player == winner else 2.0
        alpha = 1.0 if player == winner else 0.75
        ax.plot(
            player_df["turn"],
            player_df["territories"],
            marker="o",
            linewidth=line_width,
            alpha=alpha,
            color=color,
            label=player,
        )

    winner_df = turn_metrics[turn_metrics["player"] == winner].sort_values("turn")
    for _, row in winner_df.iterrows():
        if row["continents"]:
            ax.annotate(
                row["continents"],
                (row["turn"], row["territories"]),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=8,
                color="#444444",
            )

    round_starts = (
        winner_df[["turn", "round"]]
        .drop_duplicates()
        .sort_values("turn")
    )
    previous_round = None
    for _, row in round_starts.iterrows():
        if previous_round is None:
            previous_round = row["round"]
            continue
        ax.axvline(row["turn"] - 0.5, color="#bbbbbb", linestyle="--", linewidth=1)
        previous_round = row["round"]

    ax.axhline(28, color="#444444", linestyle=":", linewidth=1.5, label="65% win threshold")
    ax.set_title(title)
    ax.set_xlabel("Turn Snapshot")
    ax.set_ylabel("Territories Controlled")
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def make_combined_winner_plot(game_metrics: list[tuple[str, pd.DataFrame, str]], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    palette = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"]

    for index, (label, turn_metrics, winner) in enumerate(game_metrics):
        winner_df = turn_metrics[turn_metrics["player"] == winner].sort_values("turn")
        ax.plot(
            winner_df["turn"],
            winner_df["territories"],
            marker="o",
            linewidth=2.75,
            color=palette[index % len(palette)],
            label=f"{label}: {winner}",
        )

    ax.axhline(28, color="#444444", linestyle=":", linewidth=1.5, label="65% win threshold")
    ax.set_title("Winner Territory Growth Across Games")
    ax.set_xlabel("Turn Snapshot")
    ax.set_ylabel("Territories Controlled")
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def build_game_summary(turn_metrics: pd.DataFrame, winner: str, game_label: str) -> dict:
    winner_df = turn_metrics[turn_metrics["player"] == winner].sort_values("turn").copy()
    winner_df["territory_delta"] = winner_df["territories"].diff().fillna(0).astype(int)
    biggest_gain = winner_df.loc[winner_df["territory_delta"].idxmax()]
    end_of_round_one = winner_df[winner_df["round"] == 1].sort_values("turn").iloc[-1]

    leader_df = (
        turn_metrics.pivot(index="turn", columns="player", values="territories")
        .sort_index()
    )
    first_clear_lead_turn = None
    for turn, row in leader_df.iterrows():
        top_value = row.max()
        leaders = [player for player, value in row.items() if value == top_value]
        if winner in leaders and len(leaders) == 1:
            first_clear_lead_turn = int(turn)
            break

    return {
        "game": game_label,
        "winner": winner,
        "winner_start_territories": int(winner_df.iloc[0]["territories"]),
        "winner_end_territories": int(winner_df.iloc[-1]["territories"]),
        "winner_end_troops": int(winner_df.iloc[-1]["troops"]),
        "winner_round_1_end_territories": int(end_of_round_one["territories"]),
        "winner_round_1_end_continents": end_of_round_one["continents"].split(",")
        if end_of_round_one["continents"]
        else [],
        "winner_round_1_end_bonus": int(end_of_round_one["continent_bonus"]),
        "winner_biggest_single_turn_gain": {
            "turn": int(biggest_gain["turn"]),
            "round": int(biggest_gain["round"]),
            "territory_delta": int(biggest_gain["territory_delta"]),
            "territories_after_turn": int(biggest_gain["territories"]),
            "continents_after_turn": biggest_gain["continents"].split(",")
            if biggest_gain["continents"]
            else [],
        },
        "winner_first_clear_lead_turn": first_clear_lead_turn,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze saved Risk game folders and generate territory-control plots.")
    parser.add_argument("--output-dir", required=True, help="Directory to write plots and summaries into.")
    parser.add_argument("--game-folder", action="append", required=True, help="Saved game folder to analyze.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    game_summaries = []
    combined_inputs = []

    for index, folder_name in enumerate(args.game_folder, start=1):
        game_folder = Path(folder_name)
        end_game = json.loads((game_folder / "end_game_results.json").read_text())
        winner = end_game["winner"]
        turn_metrics = load_turn_metrics(game_folder)

        game_label = f"game_{index}"
        plot_path = output_dir / f"{game_label}_territories.png"
        make_game_plot(
            turn_metrics=turn_metrics,
            winner=winner,
            output_path=plot_path,
            title=(
                f"{game_folder.name}: territory control by turn "
                f"(winner: {winner})"
            ),
        )

        game_summaries.append(build_game_summary(turn_metrics, winner, game_folder.name))
        combined_inputs.append((game_folder.name, turn_metrics, winner))

        turn_metrics.to_csv(output_dir / f"{game_label}_turn_metrics.csv", index=False)

    combined_plot_path = output_dir / "winner_territory_growth.png"
    make_combined_winner_plot(combined_inputs, combined_plot_path)

    summary_path = output_dir / "analysis_summary.json"
    summary_path.write_text(json.dumps(game_summaries, indent=2))

    print(json.dumps(
        {
            "output_dir": str(output_dir),
            "summary_path": str(summary_path),
            "plots": [str(path) for path in sorted(output_dir.glob("*.png"))],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
