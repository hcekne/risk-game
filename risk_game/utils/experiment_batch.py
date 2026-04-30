import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

from risk_game.experiments import AgentSpec
from risk_game.game_config import GameConfig
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.paths import get_game_results_subdir
from risk_game.utils.strategic_rubric import score_turn_summary


REASONING_ORDER = ["none", "low", "medium", "high", "xhigh"]


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sanitize_path_component(value: str) -> str:
    sanitized = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            sanitized.append(char)
        else:
            sanitized.append("_")
    return "".join(sanitized).strip("_") or "unknown"


def save_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def create_experiment_folder(
    *,
    label: str,
    base_folder: str | None = None,
) -> Path:
    if base_folder is None:
        base_folder = str(get_game_results_subdir("experiments"))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_label = sanitize_path_component(label)
    folder = Path(base_folder) / f"experiment__{timestamp}__{safe_label}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def agent_spec_to_dict(spec: AgentSpec) -> Dict[str, Any]:
    return {
        "name": spec.name,
        "provider": spec.provider,
        "model": spec.model,
        "reasoning_effort": spec.reasoning_effort,
        "use_responses_api": spec.use_responses_api,
        "verbosity": spec.verbosity,
        "enable_thinking": spec.enable_thinking,
        "thinking_budget": spec.thinking_budget,
        "thinking_effort": spec.thinking_effort,
        "turn_time_limit_seconds": spec.turn_time_limit_seconds,
        "placement_time_limit_seconds": spec.placement_time_limit_seconds,
        "placement_reasoning_effort": spec.placement_reasoning_effort,
        "planning_reasoning_effort": spec.planning_reasoning_effort,
        "attack_reasoning_effort": spec.attack_reasoning_effort,
        "fortify_reasoning_effort": spec.fortify_reasoning_effort,
        "card_trade_reasoning_effort": spec.card_trade_reasoning_effort,
    }


def load_agent_specs(path: str) -> List[AgentSpec]:
    payload = json.loads(Path(path).read_text())
    if not isinstance(payload, list):
        raise ValueError("Agent specs file must contain a JSON list.")
    return [AgentSpec(**item) for item in payload]


def rotate_agent_specs(agent_specs: List[AgentSpec], game_index: int) -> List[AgentSpec]:
    if not agent_specs:
        return []
    shift = (game_index - 1) % len(agent_specs)
    return agent_specs[shift:] + agent_specs[:shift]


def build_experiment_manifest(
    *,
    label: str,
    preset_name: Optional[str],
    num_games: int,
    config: GameConfig,
    agent_specs: List[AgentSpec],
    seat_rotation_enabled: bool,
    base_folder: str,
) -> Dict[str, Any]:
    return {
        "label": label,
        "preset_name": preset_name,
        "generated_at_utc": utc_timestamp(),
        "base_folder": base_folder,
        "num_games": num_games,
        "seat_rotation_enabled": seat_rotation_enabled,
        "config": config.to_dict(),
        "agent_specs": [agent_spec_to_dict(spec) for spec in agent_specs],
    }


def build_experiment_status(
    *,
    manifest: Dict[str, Any],
    state: str,
    experiment_folder: Path,
    completed_games: int,
    current_game_index: Optional[int] = None,
    current_seat_order: Optional[List[str]] = None,
    last_completed_game_folder: Optional[str] = None,
    last_winner: Optional[str] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "label": manifest["label"],
        "preset_name": manifest.get("preset_name"),
        "state": state,
        "experiment_folder": str(experiment_folder),
        "generated_at_utc": manifest["generated_at_utc"],
        "updated_at_utc": utc_timestamp(),
        "total_games": manifest["num_games"],
        "completed_games": completed_games,
        "current_game_index": current_game_index,
        "current_seat_order": current_seat_order,
        "last_completed_game_folder": last_completed_game_folder,
        "last_winner": last_winner,
        "error": error,
    }


def write_experiment_manifest(experiment_folder: Path, manifest: Dict[str, Any]) -> Path:
    return save_json(experiment_folder / "experiment_manifest.json", manifest)


def write_experiment_status(experiment_folder: Path, status: Dict[str, Any]) -> Path:
    return save_json(experiment_folder / "experiment_status.json", status)


def write_experiment_results(experiment_folder: Path, results: List[Dict[str, Any]]) -> Path:
    return save_json(experiment_folder / "experiment_results.json", {"results": results})


def cap_reasoning_effort(requested_effort: str, max_effort: str) -> str:
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
    return REASONING_ORDER[
        min(REASONING_ORDER.index(requested_effort), REASONING_ORDER.index(max_effort))
    ]


def resolve_phase_reasoning_effort(
    requested_effort: str,
    explicit_effort: Optional[str],
    max_effort: str,
) -> str:
    if explicit_effort is not None:
        return explicit_effort
    return cap_reasoning_effort(requested_effort, max_effort)


def run_agent_preflight(agent_specs: List[AgentSpec], timeout_seconds: float = 30.0) -> List[Dict[str, Any]]:
    checked = set()
    results = []
    for spec in agent_specs:
        key = (
            spec.provider,
            spec.model,
            spec.reasoning_effort,
            spec.verbosity,
            spec.enable_thinking,
            spec.thinking_budget,
            spec.thinking_effort,
        )
        if key in checked:
            continue
        checked.add(key)

        client = create_llm_client(
            spec.provider,
            spec.model,
            use_responses_api=spec.use_responses_api,
            reasoning_effort=spec.reasoning_effort,
            verbosity=spec.verbosity,
            enable_thinking=spec.enable_thinking,
            thinking_budget=spec.thinking_budget,
            thinking_effort=spec.thinking_effort,
        )
        started_at = datetime.now(timezone.utc)
        response = client.get_chat_completion(
            "Reply with exactly OK.",
            reasoning_effort=spec.reasoning_effort,
            timeout_seconds=timeout_seconds,
            max_attempts_override=1,
        )
        results.append(
            {
                "provider": spec.provider,
                "model": spec.model,
                "name": spec.name,
                "started_at_utc": started_at.replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "response_preview": response.strip()[:80],
                "timeout_seconds": timeout_seconds,
            }
        )
    return results


def _rounded_mean(values: Iterable[float], digits: int = 2) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return round(mean(values), digits)


def _summarize_player_turns(game: Any, player_name: str) -> Dict[str, Any]:
    player_turns = [
        turn_summary
        for turn_summary in getattr(game, "turn_summaries", [])
        if turn_summary["player"]["name"] == player_name
    ]
    scored_turns = []
    for turn_summary in player_turns:
        if "rubric" not in turn_summary:
            turn_summary["rubric"] = score_turn_summary(turn_summary)
        scored_turns.append(turn_summary)

    strategic_scores = [
        turn_summary["rubric"]["overall_score"] for turn_summary in scored_turns
    ]
    fallback_count = sum(
        1
        for turn_summary in scored_turns
        for decision in turn_summary.get("llm_decisions", [])
        if decision.get("used_fallback_response")
    )
    return {
        "average_strategic_score": _rounded_mean(strategic_scores),
        "fallback_count": fallback_count,
    }


def build_game_result(
    game: Any,
    *,
    game_index: int,
    game_folder: str,
    elapsed_seconds: float,
    seat_order: List[str],
) -> Dict[str, Any]:
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
        player_turn_summary = _summarize_player_turns(game, player_name)
        strategic_scores[player_name] = player_turn_summary["average_strategic_score"]
        llm_fallback_counts[player_name] = player_turn_summary["fallback_count"]

    return {
        "game_index": game_index,
        "winner": game.winner.name if game.winner else None,
        "victory_condition": game.victory_condition,
        "rounds": game.game_round,
        "elapsed_seconds": round(elapsed_seconds, 2),
        "territories": territories,
        "turn_times": turn_times,
        "error_counts": error_counts,
        "strategic_scores": strategic_scores,
        "llm_fallback_counts": llm_fallback_counts,
        "seat_order": seat_order,
        "game_folder": game_folder,
    }


def compute_experiment_summary(
    manifest: Dict[str, Any],
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    win_counts: Counter[str] = Counter()
    victory_counts: Counter[str] = Counter()
    per_player: Dict[str, Dict[str, List[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for result in results:
        winner = result.get("winner")
        if winner:
            win_counts[winner] += 1
        victory_condition = result.get("victory_condition")
        if victory_condition:
            victory_counts[victory_condition] += 1

        for player_name, territories in result.get("territories", {}).items():
            per_player[player_name]["territories"].append(territories)
        for player_name, turn_time in result.get("turn_times", {}).items():
            per_player[player_name]["turn_times"].append(turn_time)
        for player_name, score in result.get("strategic_scores", {}).items():
            if score is not None:
                per_player[player_name]["strategic_scores"].append(score)
        for player_name, fallback_count in result.get("llm_fallback_counts", {}).items():
            per_player[player_name]["fallback_counts"].append(fallback_count)
        for player_name, error_bundle in result.get("error_counts", {}).items():
            for error_name, count in error_bundle.items():
                per_player[player_name][f"error_{error_name}"].append(count)

    players_summary = {}
    for player_name, metrics in per_player.items():
        players_summary[player_name] = {
            "wins": win_counts.get(player_name, 0),
            "mean_final_territories": _rounded_mean(metrics["territories"]),
            "mean_turn_time_seconds": _rounded_mean(metrics["turn_times"]),
            "mean_strategic_score": _rounded_mean(metrics["strategic_scores"]),
            "mean_fallback_count": _rounded_mean(metrics["fallback_counts"]),
            "mean_placement_errors": _rounded_mean(metrics["error_placement"]),
            "mean_attack_errors": _rounded_mean(metrics["error_attack"]),
            "mean_fortify_errors": _rounded_mean(metrics["error_fortify"]),
            "mean_card_trade_errors": _rounded_mean(metrics["error_card_trade"]),
            "mean_formatting_errors": _rounded_mean(metrics["error_formatting"]),
        }

    return {
        "label": manifest["label"],
        "preset_name": manifest.get("preset_name"),
        "num_games_completed": len(results),
        "num_games_planned": manifest["num_games"],
        "seat_rotation_enabled": manifest["seat_rotation_enabled"],
        "mean_rounds": _rounded_mean(result["rounds"] for result in results),
        "mean_elapsed_seconds": _rounded_mean(
            result["elapsed_seconds"] for result in results
        ),
        "win_counts": dict(win_counts),
        "victory_conditions": dict(victory_counts),
        "players": players_summary,
        "game_folders": [result["game_folder"] for result in results],
    }


def render_experiment_summary_markdown(
    manifest: Dict[str, Any],
    summary: Dict[str, Any],
) -> str:
    lines = [
        "# Experiment Summary",
        "",
        f"- Label: {manifest['label']}",
        f"- Preset: {manifest.get('preset_name') or 'custom'}",
        f"- Games completed: {summary['num_games_completed']} / {summary['num_games_planned']}",
        f"- Seat rotation: {summary['seat_rotation_enabled']}",
        f"- Mean rounds: {summary.get('mean_rounds')}",
        f"- Mean elapsed seconds: {summary.get('mean_elapsed_seconds')}",
        "",
        "## Win Counts",
    ]
    if summary["win_counts"]:
        for player_name, wins in sorted(
            summary["win_counts"].items(), key=lambda item: (-item[1], item[0])
        ):
            lines.append(f"- {player_name}: {wins}")
    else:
        lines.append("- No completed games yet.")

    lines.extend(["", "## Player Metrics"])
    for player_name, metrics in sorted(summary["players"].items()):
        lines.append(f"### {player_name}")
        lines.append(f"- Wins: {metrics['wins']}")
        lines.append(f"- Mean final territories: {metrics['mean_final_territories']}")
        lines.append(f"- Mean turn time seconds: {metrics['mean_turn_time_seconds']}")
        lines.append(f"- Mean strategic score: {metrics['mean_strategic_score']}")
        lines.append(f"- Mean fallback count: {metrics['mean_fallback_count']}")
        lines.append(f"- Mean placement errors: {metrics['mean_placement_errors']}")
        lines.append(f"- Mean attack errors: {metrics['mean_attack_errors']}")
        lines.append(f"- Mean fortify errors: {metrics['mean_fortify_errors']}")
        lines.append(f"- Mean card-trade errors: {metrics['mean_card_trade_errors']}")
        lines.append(f"- Mean formatting errors: {metrics['mean_formatting_errors']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def find_latest_experiment_folder(base_folder: str | None = None) -> Path:
    if base_folder is None:
        base_folder = str(get_game_results_subdir("experiments"))
    base_path = Path(base_folder)
    candidates = sorted(
        [path for path in base_path.glob("experiment__*") if path.is_dir()],
        key=lambda path: path.name,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No experiment folders found under {base_path.resolve()}"
        )
    return candidates[-1]


def load_experiment_context(experiment_folder: str) -> Dict[str, Any]:
    folder = Path(experiment_folder)
    manifest = load_json(folder / "experiment_manifest.json")
    status = load_json(folder / "experiment_status.json")
    results_path = folder / "experiment_results.json"
    results_payload = load_json(results_path) if results_path.exists() else {"results": []}
    return {
        "experiment_folder": folder,
        "manifest": manifest,
        "status": status,
        "results": results_payload.get("results", []),
    }


def build_series_manifest(
    *,
    label: str,
    contexts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not contexts:
        raise ValueError("At least one experiment context is required.")

    reference_manifest = contexts[0]["manifest"]
    reference_agent_specs = reference_manifest["agent_specs"]
    reference_config = reference_manifest["config"]
    reference_seat_rotation = reference_manifest["seat_rotation_enabled"]

    total_planned_games = 0
    source_experiments = []
    for context in contexts:
        manifest = context["manifest"]
        if manifest["agent_specs"] != reference_agent_specs:
            raise ValueError(
                "Cannot combine experiment folders with different agent specs."
            )
        if manifest["config"] != reference_config:
            raise ValueError(
                "Cannot combine experiment folders with different game configs."
            )
        if manifest["seat_rotation_enabled"] != reference_seat_rotation:
            raise ValueError(
                "Cannot combine experiment folders with different seat-rotation settings."
            )
        total_planned_games += manifest["num_games"]
        source_experiments.append(
            {
                "folder": str(context["experiment_folder"]),
                "label": manifest["label"],
                "preset_name": manifest.get("preset_name"),
                "num_games_planned": manifest["num_games"],
                "num_games_completed": len(context["results"]),
                "generated_at_utc": manifest["generated_at_utc"],
            }
        )

    return {
        "label": label,
        "preset_name": reference_manifest.get("preset_name"),
        "generated_at_utc": utc_timestamp(),
        "base_folder": str(get_game_results_subdir("experiment_series")),
        "num_games": total_planned_games,
        "seat_rotation_enabled": reference_seat_rotation,
        "config": reference_config,
        "agent_specs": reference_agent_specs,
        "source_experiments": source_experiments,
    }


def combine_experiment_results(contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    combined_results: List[Dict[str, Any]] = []
    combined_index = 1
    for context in contexts:
        source_folder = str(context["experiment_folder"])
        for result in context["results"]:
            combined_result = dict(result)
            combined_result["source_experiment_folder"] = source_folder
            combined_result["source_game_index"] = result.get("game_index")
            combined_result["game_index"] = combined_index
            combined_results.append(combined_result)
            combined_index += 1
    return combined_results


def build_status_line(status: Dict[str, Any]) -> str:
    line = (
        f"{status['label']} state={status['state']} "
        f"games={status['completed_games']}/{status['total_games']}"
    )
    if status.get("current_game_index") is not None:
        line += f" current={status['current_game_index']}"
    if status.get("last_winner"):
        line += f" last_winner={status['last_winner']}"
    if status.get("error"):
        line += f" error={status['error']}"
    line += f" updated={status['updated_at_utc']}"
    return line
