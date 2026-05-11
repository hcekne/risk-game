import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


SHARED_RESULTS_PREFIX = "/shared-game-results/"
HOST_SHARED_RESULTS_ROOT = Path("/home/hcekne/shared/risk-game/game_results")

PLANNING_PATTERNS = {
    "explicit_endgame_goal": re.compile(
        r"\bwin\b|65%|28/42|\btarget\b|need \d+ more|win target",
        re.IGNORECASE,
    ),
    "quantified_goal": re.compile(
        r"need \d+ more|\d+ more territories|\b28\b|\b27\b|\b65%\b|\b\d+ cheap territories?\b",
        re.IGNORECASE,
    ),
    "aggressive_action": re.compile(
        r"\b(clear|sweep|eliminate|break|secure|finish|close|push|blitz)\b",
        re.IGNORECASE,
    ),
    "contingency": re.compile(
        r"\b(if|otherwise|backup|secondary|fallback|avoid|skip)\b",
        re.IGNORECASE,
    ),
    "card_focus": re.compile(r"\bcard\b", re.IGNORECASE),
    "continent_focus": re.compile(
        r"\b(australia|asia|africa|europe|north america|south america|continent bonus|bonus)\b",
        re.IGNORECASE,
    ),
}


def resolve_host_path(path_str: str) -> Path:
    if path_str.startswith(SHARED_RESULTS_PREFIX):
        suffix = path_str[len(SHARED_RESULTS_PREFIX) :]
        return HOST_SHARED_RESULTS_ROOT / suffix
    return Path(path_str)


def load_series_results(path: Path) -> list[dict]:
    with path.open() as f:
        return json.load(f)["results"]


def load_turn_summaries(game_folder: str) -> list[dict]:
    folder = resolve_host_path(game_folder)
    summary_files = sorted(
        folder.glob("turn_summary_turn_*.json"),
        key=lambda item: int(item.stem.split("_")[-1]),
    )
    return [json.loads(path.read_text()) for path in summary_files]


def round_float(value: float) -> float:
    return round(float(value), 3)


def safe_mean(total: float, count: int) -> float | None:
    if not count:
        return None
    return round_float(total / count)


def safe_share(count: int, total: int) -> float | None:
    if not total:
        return None
    return round_float(count / total)


def territory_band(territories: int) -> str:
    if territories <= 9:
        return "early_0_9"
    if territories <= 19:
        return "mid_10_19"
    return "late_20_plus"


def analyze_planning(turn_records: list[dict]) -> dict:
    per_player = defaultdict(
        lambda: {
            "plan_count": 0,
            "word_count_total": 0,
            "territory_delta_total": 0,
            "successful_attack_total": 0,
            "feature_plan_counts": Counter(),
            "feature_token_counts": Counter(),
            "goal_turns": 0,
            "goal_territory_delta_total": 0,
            "goal_successful_attack_total": 0,
            "non_goal_turns": 0,
            "non_goal_territory_delta_total": 0,
            "non_goal_successful_attack_total": 0,
            "band_counts": defaultdict(int),
            "band_goal_counts": defaultdict(int),
            "examples": defaultdict(list),
        }
    )

    pooled = {
        "explicit_goal_turns": 0,
        "explicit_goal_territory_delta_total": 0,
        "explicit_goal_successful_attack_total": 0,
        "non_goal_turns": 0,
        "non_goal_territory_delta_total": 0,
        "non_goal_successful_attack_total": 0,
    }

    for record in turn_records:
        player = record["player"]
        text = record["plan_text"].strip()
        if not text:
            continue

        words = re.findall(r"\b\w+(?:-\w+)?\b", text.lower())
        word_count = len(words)
        stats = per_player[player]
        stats["plan_count"] += 1
        stats["word_count_total"] += word_count
        stats["territory_delta_total"] += record["territory_delta"]
        stats["successful_attack_total"] += record["successful_attack_count"]

        band = territory_band(record["start_territories"])
        stats["band_counts"][band] += 1

        explicit_goal = False
        for feature_name, pattern in PLANNING_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                stats["feature_plan_counts"][feature_name] += 1
                stats["feature_token_counts"][feature_name] += len(matches)
                if feature_name == "explicit_endgame_goal":
                    explicit_goal = True
                    stats["band_goal_counts"][band] += 1
                    if len(stats["examples"][feature_name]) < 3:
                        stats["examples"][feature_name].append(text)

        if explicit_goal:
            stats["goal_turns"] += 1
            stats["goal_territory_delta_total"] += record["territory_delta"]
            stats["goal_successful_attack_total"] += record["successful_attack_count"]
            pooled["explicit_goal_turns"] += 1
            pooled["explicit_goal_territory_delta_total"] += record["territory_delta"]
            pooled["explicit_goal_successful_attack_total"] += record[
                "successful_attack_count"
            ]
        else:
            stats["non_goal_turns"] += 1
            stats["non_goal_territory_delta_total"] += record["territory_delta"]
            stats["non_goal_successful_attack_total"] += record["successful_attack_count"]
            pooled["non_goal_turns"] += 1
            pooled["non_goal_territory_delta_total"] += record["territory_delta"]
            pooled["non_goal_successful_attack_total"] += record[
                "successful_attack_count"
            ]

    output = {"players": {}, "pooled_goal_effect": {}}
    for player, stats in per_player.items():
        plan_count = stats["plan_count"]
        word_count_total = stats["word_count_total"]
        feature_metrics = {}
        for feature_name in PLANNING_PATTERNS:
            feature_metrics[feature_name] = {
                "plan_share": safe_share(
                    stats["feature_plan_counts"][feature_name], plan_count
                ),
                "count_per_100_words": safe_mean(
                    stats["feature_token_counts"][feature_name] * 100,
                    word_count_total,
                ),
            }

        output["players"][player] = {
            "plan_count": plan_count,
            "avg_words_per_plan": safe_mean(word_count_total, plan_count),
            "avg_territory_delta_per_plan": safe_mean(
                stats["territory_delta_total"], plan_count
            ),
            "avg_successful_attacks_per_plan": safe_mean(
                stats["successful_attack_total"], plan_count
            ),
            "feature_metrics": feature_metrics,
            "explicit_goal_turns": stats["goal_turns"],
            "avg_territory_delta_when_explicit_goal": safe_mean(
                stats["goal_territory_delta_total"], stats["goal_turns"]
            ),
            "avg_successful_attacks_when_explicit_goal": safe_mean(
                stats["goal_successful_attack_total"], stats["goal_turns"]
            ),
            "avg_territory_delta_without_explicit_goal": safe_mean(
                stats["non_goal_territory_delta_total"], stats["non_goal_turns"]
            ),
            "avg_successful_attacks_without_explicit_goal": safe_mean(
                stats["non_goal_successful_attack_total"], stats["non_goal_turns"]
            ),
            "goal_share_by_start_territory_band": {
                band: safe_share(
                    stats["band_goal_counts"][band], stats["band_counts"][band]
                )
                for band in ("early_0_9", "mid_10_19", "late_20_plus")
                if stats["band_counts"][band]
            },
            "examples": {
                key: value
                for key, value in stats["examples"].items()
                if value
            },
        }

    output["pooled_goal_effect"] = {
        "explicit_goal_turns": pooled["explicit_goal_turns"],
        "avg_territory_delta_when_explicit_goal": safe_mean(
            pooled["explicit_goal_territory_delta_total"],
            pooled["explicit_goal_turns"],
        ),
        "avg_successful_attacks_when_explicit_goal": safe_mean(
            pooled["explicit_goal_successful_attack_total"],
            pooled["explicit_goal_turns"],
        ),
        "non_goal_turns": pooled["non_goal_turns"],
        "avg_territory_delta_without_explicit_goal": safe_mean(
            pooled["non_goal_territory_delta_total"], pooled["non_goal_turns"]
        ),
        "avg_successful_attacks_without_explicit_goal": safe_mean(
            pooled["non_goal_successful_attack_total"], pooled["non_goal_turns"]
        ),
    }
    return output


def analyze_execution(turn_records: list[dict]) -> dict:
    per_player = defaultdict(
        lambda: {
            "turn_count": 0,
            "turns_with_exec_fallback": 0,
            "turns_with_invalid_action": 0,
            "attack_turns": 0,
            "zero_attack_turns": 0,
            "long_chain_ge4_turns": 0,
            "long_chain_ge6_turns": 0,
            "big_delta_ge4_turns": 0,
            "big_delta_ge6_turns": 0,
            "midgame_turns": 0,
            "midgame_territory_delta_total": 0,
            "midgame_successful_attack_total": 0,
            "midgame_ge4_turns": 0,
            "phase_decision_counts": Counter(),
            "phase_fallback_counts": Counter(),
            "phase_invalid_counts": Counter(),
            "attack_bucket_counts": Counter(),
        }
    )

    for record in turn_records:
        player = record["player"]
        stats = per_player[player]
        stats["turn_count"] += 1

        successful = record["successful_attack_count"]
        failed = record["failed_attack_count"]
        total_attacks = successful + failed

        if total_attacks > 0:
            stats["attack_turns"] += 1
        else:
            stats["zero_attack_turns"] += 1

        if successful >= 4:
            stats["long_chain_ge4_turns"] += 1
        if successful >= 6:
            stats["long_chain_ge6_turns"] += 1
        if record["territory_delta"] >= 4:
            stats["big_delta_ge4_turns"] += 1
        if record["territory_delta"] >= 6:
            stats["big_delta_ge6_turns"] += 1

        if successful == 0:
            bucket = "0"
        elif successful == 1:
            bucket = "1"
        elif successful <= 3:
            bucket = "2_3"
        elif successful <= 5:
            bucket = "4_5"
        else:
            bucket = "6_plus"
        stats["attack_bucket_counts"][bucket] += 1

        if 10 <= record["start_territories"] <= 19:
            stats["midgame_turns"] += 1
            stats["midgame_territory_delta_total"] += record["territory_delta"]
            stats["midgame_successful_attack_total"] += successful
            if record["territory_delta"] >= 4:
                stats["midgame_ge4_turns"] += 1

        saw_exec_fallback = False
        for decision in record["llm_decisions"]:
            phase = decision.get("phase")
            if phase == "pre_turn_planning":
                continue
            stats["phase_decision_counts"][phase] += 1
            if decision.get("used_fallback_response"):
                stats["phase_fallback_counts"][phase] += 1
                saw_exec_fallback = True

        for event in record["events"]:
            phase = event.get("phase")
            if phase == "pre_turn_planning":
                continue
            if event.get("valid") is False:
                stats["phase_invalid_counts"][phase] += 1

        if saw_exec_fallback:
            stats["turns_with_exec_fallback"] += 1
        if record["invalid_action_count"] > 0:
            stats["turns_with_invalid_action"] += 1

    output = {"players": {}}
    for player, stats in per_player.items():
        turn_count = stats["turn_count"]
        phase_metrics = {}
        for phase in (
            "troop_placement",
            "attack",
            "fortify",
            "optional_card_trade",
            "mandatory_card_trade",
        ):
            decisions = stats["phase_decision_counts"][phase]
            if not decisions:
                continue
            phase_metrics[phase] = {
                "decision_count": decisions,
                "fallback_rate": safe_share(
                    stats["phase_fallback_counts"][phase], decisions
                ),
                "invalid_rate": safe_share(
                    stats["phase_invalid_counts"][phase], decisions
                ),
            }

        output["players"][player] = {
            "turn_count": turn_count,
            "turns_with_exec_fallback_share": safe_share(
                stats["turns_with_exec_fallback"], turn_count
            ),
            "turns_with_invalid_action_share": safe_share(
                stats["turns_with_invalid_action"], turn_count
            ),
            "attack_turn_share": safe_share(stats["attack_turns"], turn_count),
            "zero_attack_turn_share": safe_share(stats["zero_attack_turns"], turn_count),
            "long_chain_ge4_turn_share": safe_share(
                stats["long_chain_ge4_turns"], turn_count
            ),
            "long_chain_ge6_turn_share": safe_share(
                stats["long_chain_ge6_turns"], turn_count
            ),
            "big_delta_ge4_turn_share": safe_share(
                stats["big_delta_ge4_turns"], turn_count
            ),
            "big_delta_ge6_turn_share": safe_share(
                stats["big_delta_ge6_turns"], turn_count
            ),
            "midgame_avg_territory_delta": safe_mean(
                stats["midgame_territory_delta_total"], stats["midgame_turns"]
            ),
            "midgame_avg_successful_attacks": safe_mean(
                stats["midgame_successful_attack_total"], stats["midgame_turns"]
            ),
            "midgame_ge4_turn_share": safe_share(
                stats["midgame_ge4_turns"], stats["midgame_turns"]
            ),
            "attack_chain_distribution": {
                bucket: safe_share(stats["attack_bucket_counts"][bucket], turn_count)
                for bucket in ("0", "1", "2_3", "4_5", "6_plus")
            },
            "phase_metrics": phase_metrics,
        }
    return output


def collect_turn_records(series_results: list[dict]) -> list[dict]:
    turn_records = []
    for game in series_results:
        winner = game["winner"]
        for turn_summary in load_turn_summaries(game["game_folder"]):
            turn_records.append(
                {
                    "game_folder": game["game_folder"],
                    "winner": winner,
                    "player": turn_summary["player"]["name"],
                    "plan_text": turn_summary.get("plan", {}).get("text", ""),
                    "start_territories": turn_summary["pre_turn"]["player_state"][
                        "territories"
                    ],
                    "territory_delta": turn_summary["derived"]["territory_delta"],
                    "successful_attack_count": turn_summary["derived"][
                        "successful_attack_count"
                    ],
                    "failed_attack_count": turn_summary["derived"][
                        "failed_attack_count"
                    ],
                    "invalid_action_count": turn_summary["derived"][
                        "invalid_action_count"
                    ],
                    "events": turn_summary["events"],
                    "llm_decisions": turn_summary["llm_decisions"],
                }
            )
    return turn_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze planning and execution trace patterns from a saved pooled experiment series."
    )
    parser.add_argument(
        "--series-results",
        required=True,
        help="Path to series_results.json for the pooled experiment.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write planning and execution analysis JSON files into.",
    )
    args = parser.parse_args()

    series_results = load_series_results(Path(args.series_results))
    turn_records = collect_turn_records(series_results)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    planning = analyze_planning(turn_records)
    execution = analyze_execution(turn_records)

    planning_path = output_dir / "planning_trace_metrics.json"
    planning_path.write_text(json.dumps(planning, indent=2))

    execution_path = output_dir / "execution_trace_metrics.json"
    execution_path.write_text(json.dumps(execution, indent=2))

    print(
        json.dumps(
            {
                "series_results": str(args.series_results),
                "turn_record_count": len(turn_records),
                "planning_trace_metrics": str(planning_path),
                "execution_trace_metrics": str(execution_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
