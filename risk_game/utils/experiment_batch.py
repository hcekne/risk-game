import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable, Dict, Iterable, List, Optional

from risk_game.experiments import (
    AgentSpec,
    agent_spec_has_planning_client_override,
    planning_client_config_from_spec,
    primary_client_config_from_spec,
)
from risk_game.game_config import GameConfig
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.paths import get_game_results_subdir
from risk_game.utils.model_pricing import (
    PRICING_SNAPSHOT_ID,
    estimate_usage_cost_usd,
)
from risk_game.utils.provider_pause import detect_provider_pause_signal
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
        "planning_provider": spec.planning_provider,
        "planning_model": spec.planning_model,
        "planning_use_responses_api": spec.planning_use_responses_api,
        "planning_verbosity": spec.planning_verbosity,
        "planning_enable_thinking": spec.planning_enable_thinking,
        "planning_thinking_budget": spec.planning_thinking_budget,
        "planning_thinking_effort": spec.planning_thinking_effort,
        "turn_time_limit_seconds": spec.turn_time_limit_seconds,
        "planning_time_limit_seconds": spec.planning_time_limit_seconds,
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


def run_agent_preflight(
    agent_specs: List[AgentSpec],
    timeout_seconds: float = 30.0,
    pause_handler: Optional[Callable[[Dict[str, object]], None]] = None,
) -> List[Dict[str, Any]]:
    checked = set()
    results = []
    for spec in agent_specs:
        client_configs = [("primary", primary_client_config_from_spec(spec))]
        if agent_spec_has_planning_client_override(spec):
            planning_config = planning_client_config_from_spec(spec)
            if planning_config is not None:
                client_configs.append(("planning", planning_config))

        for client_role, client_config in client_configs:
            key = (
                client_config["provider"],
                client_config["model"],
                client_config["reasoning_effort"],
                client_config["verbosity"],
                client_config["enable_thinking"],
                client_config["thinking_budget"],
                client_config["thinking_effort"],
                client_config["use_responses_api"],
            )
            if key in checked:
                continue
            checked.add(key)

            client = create_llm_client(
                client_config["provider"],
                client_config["model"],
                use_responses_api=client_config["use_responses_api"],
                reasoning_effort=client_config["reasoning_effort"],
                verbosity=client_config["verbosity"],
                enable_thinking=client_config["enable_thinking"],
                thinking_budget=client_config["thinking_budget"],
                thinking_effort=client_config["thinking_effort"],
            )
            started_at = datetime.now(timezone.utc)
            while True:
                try:
                    response = client.get_chat_completion(
                        "Reply with exactly OK.",
                        reasoning_effort=client_config["reasoning_effort"],
                        timeout_seconds=timeout_seconds,
                        max_attempts_override=1,
                    )
                    break
                except Exception as exc:
                    error = str(exc)[:1200]
                    pause_signal = detect_provider_pause_signal(error)
                    if pause_signal is None or pause_handler is None:
                        raise
                    pause_handler(
                        {
                            "signal": pause_signal,
                            "provider": client_config["provider"],
                            "model": client_config["model"],
                            "player_name": spec.name,
                            "phase": "preflight",
                            "client_role": client_role,
                            "scope": "preflight",
                            "error": error,
                        }
                    )
                    started_at = datetime.now(timezone.utc)
            results.append(
                {
                    "provider": client_config["provider"],
                    "model": client_config["model"],
                    "name": spec.name,
                    "client_role": client_role,
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


def _build_turn_metric_summary_from_turn_summaries(
    player_turns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    successful_attack_counts = [
        turn_summary.get("derived", {}).get("successful_attack_count", 0)
        for turn_summary in player_turns
    ]
    failed_attack_counts = [
        turn_summary.get("derived", {}).get("failed_attack_count", 0)
        for turn_summary in player_turns
    ]
    territory_deltas = [
        turn_summary.get("derived", {}).get("territory_delta", 0)
        for turn_summary in player_turns
    ]
    timed_out_turn_count = sum(
        1
        for turn_summary in player_turns
        if turn_summary.get("derived", {}).get("turn_timed_out", False)
    )
    attacking_turn_count = sum(1 for count in successful_attack_counts if count > 0)
    average_successful_attacks_per_attacking_turn = None
    if attacking_turn_count:
        average_successful_attacks_per_attacking_turn = round(
            sum(successful_attack_counts) / attacking_turn_count,
            3,
        )
    return {
        "total_successful_attacks": sum(successful_attack_counts),
        "total_failed_attacks": sum(failed_attack_counts),
        "average_successful_attacks_per_turn": _rounded_mean(
            successful_attack_counts,
            digits=3,
        ),
        "average_successful_attacks_per_attacking_turn": (
            average_successful_attacks_per_attacking_turn
        ),
        "attack_turn_rate": round(
            attacking_turn_count / len(player_turns),
            3,
        )
        if player_turns
        else None,
        "average_territory_delta_per_turn": _rounded_mean(
            territory_deltas,
            digits=3,
        ),
        "timed_out_turn_count": timed_out_turn_count,
    }


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
    turn_metric_summary = _build_turn_metric_summary_from_turn_summaries(scored_turns)
    return {
        "average_strategic_score": _rounded_mean(strategic_scores),
        "fallback_count": fallback_count,
        **turn_metric_summary,
    }


def _load_turn_metrics_from_saved_game_folder(game_folder: str) -> Dict[str, Dict[str, Any]]:
    folder = Path(game_folder)
    if not folder.exists():
        return {}
    per_player_turns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for turn_summary_path in sorted(folder.glob("turn_summary_turn_*.json")):
        turn_summary = load_json(turn_summary_path)
        player_name = turn_summary.get("player", {}).get("name")
        if player_name is None:
            continue
        per_player_turns[player_name].append(turn_summary)
    return {
        player_name: _build_turn_metric_summary_from_turn_summaries(player_turns)
        for player_name, player_turns in per_player_turns.items()
    }


def _llm_interactions_folder_for_game(game_folder: str) -> Path:
    folder = Path(game_folder)
    return folder.parent / "llm_interactions" / folder.name


def _blank_usage_bucket() -> Dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_tokens": 0,
        "interaction_count": 0,
        "estimated_total_cost_usd": 0.0,
        "by_client": {},
        "missing_pricing_models": set(),
    }


def _normalize_token_count(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _accumulate_usage_bucket(
    bucket: Dict[str, Any],
    *,
    provider: Optional[str],
    model: Optional[str],
    client_role: Optional[str],
    usage: Dict[str, Any],
) -> None:
    input_tokens = _normalize_token_count(usage.get("input_tokens"))
    output_tokens = _normalize_token_count(usage.get("output_tokens"))
    total_tokens = _normalize_token_count(usage.get("total_tokens"))
    cached_input_tokens = _normalize_token_count(usage.get("cached_input_tokens"))
    reasoning_tokens = _normalize_token_count(usage.get("reasoning_tokens"))

    if total_tokens == 0 and (input_tokens or output_tokens):
        total_tokens = input_tokens + output_tokens

    bucket["input_tokens"] += input_tokens
    bucket["output_tokens"] += output_tokens
    bucket["total_tokens"] += total_tokens
    bucket["cached_input_tokens"] += cached_input_tokens
    bucket["reasoning_tokens"] += reasoning_tokens
    bucket["interaction_count"] += 1

    client_key = f"{provider}:{model}:{client_role or 'unknown'}"
    by_client = bucket["by_client"]
    client_bucket = by_client.setdefault(
        client_key,
        {
            "provider": provider,
            "model": model,
            "client_role": client_role,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cached_input_tokens": 0,
            "reasoning_tokens": 0,
            "interaction_count": 0,
            "estimated_total_cost_usd": 0.0,
        },
    )
    client_bucket["input_tokens"] += input_tokens
    client_bucket["output_tokens"] += output_tokens
    client_bucket["total_tokens"] += total_tokens
    client_bucket["cached_input_tokens"] += cached_input_tokens
    client_bucket["reasoning_tokens"] += reasoning_tokens
    client_bucket["interaction_count"] += 1

    cost_estimate = estimate_usage_cost_usd(
        provider=provider,
        model=model,
        usage=usage,
    )
    if cost_estimate is None:
        if provider and model:
            bucket["missing_pricing_models"].add(f"{provider}:{model}")
        return

    total_cost_usd = float(cost_estimate["total_cost_usd"])
    bucket["estimated_total_cost_usd"] += total_cost_usd
    client_bucket["estimated_total_cost_usd"] += total_cost_usd


def _freeze_usage_bucket(bucket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "input_tokens": bucket["input_tokens"],
        "output_tokens": bucket["output_tokens"],
        "total_tokens": bucket["total_tokens"],
        "cached_input_tokens": bucket["cached_input_tokens"],
        "reasoning_tokens": bucket["reasoning_tokens"],
        "interaction_count": bucket["interaction_count"],
        "estimated_total_cost_usd": round(bucket["estimated_total_cost_usd"], 8),
        "by_client": sorted(
            (
                {
                    **client_bucket,
                    "estimated_total_cost_usd": round(
                        client_bucket["estimated_total_cost_usd"], 8
                    ),
                }
                for client_bucket in bucket["by_client"].values()
            ),
            key=lambda item: (
                -(item["estimated_total_cost_usd"] or 0.0),
                item.get("provider") or "",
                item.get("model") or "",
                item.get("client_role") or "",
            ),
        ),
        "missing_pricing_models": sorted(bucket["missing_pricing_models"]),
    }


def _load_usage_metrics_from_saved_game_folder(
    game_folder: str,
) -> Dict[str, Dict[str, Any]]:
    interactions_folder = _llm_interactions_folder_for_game(game_folder)
    if not interactions_folder.exists():
        return {}

    per_player_usage: Dict[str, Dict[str, Any]] = defaultdict(_blank_usage_bucket)
    for interaction_path in sorted(interactions_folder.rglob("*.json")):
        interaction = load_json(interaction_path)
        if interaction.get("entry_type") == "provider_pause_error":
            continue
        player_name = interaction.get("player")
        usage = interaction.get("response", {}).get("usage")
        if player_name is None or not isinstance(usage, dict):
            continue
        _accumulate_usage_bucket(
            per_player_usage[player_name],
            provider=interaction.get("provider"),
            model=interaction.get("model"),
            client_role=interaction.get("client_role"),
            usage=usage,
        )

    return {
        player_name: _freeze_usage_bucket(bucket)
        for player_name, bucket in per_player_usage.items()
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
    turn_metrics = {}
    for player_name in territories:
        player_turn_summary = _summarize_player_turns(game, player_name)
        strategic_scores[player_name] = player_turn_summary["average_strategic_score"]
        llm_fallback_counts[player_name] = player_turn_summary["fallback_count"]
        turn_metrics[player_name] = {
            "total_successful_attacks": player_turn_summary["total_successful_attacks"],
            "total_failed_attacks": player_turn_summary["total_failed_attacks"],
            "average_successful_attacks_per_turn": player_turn_summary[
                "average_successful_attacks_per_turn"
            ],
            "average_successful_attacks_per_attacking_turn": player_turn_summary[
                "average_successful_attacks_per_attacking_turn"
            ],
            "attack_turn_rate": player_turn_summary["attack_turn_rate"],
            "average_territory_delta_per_turn": player_turn_summary[
                "average_territory_delta_per_turn"
            ],
            "timed_out_turn_count": player_turn_summary["timed_out_turn_count"],
        }
    usage_metrics = _load_usage_metrics_from_saved_game_folder(game_folder)

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
        "turn_metrics": turn_metrics,
        "usage_metrics": usage_metrics,
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
    per_player_usage_breakdown: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    per_player_missing_pricing: Dict[str, set[str]] = defaultdict(set)
    total_input_tokens = 0
    total_output_tokens = 0
    total_reasoning_tokens = 0
    total_estimated_cost_usd = 0.0
    summary_missing_pricing_models: set[str] = set()

    for result in results:
        turn_metrics = result.get("turn_metrics")
        if turn_metrics is None and result.get("game_folder"):
            turn_metrics = _load_turn_metrics_from_saved_game_folder(
                result["game_folder"]
            )
        usage_metrics = result.get("usage_metrics")
        if usage_metrics is None and result.get("game_folder"):
            usage_metrics = _load_usage_metrics_from_saved_game_folder(
                result["game_folder"]
            )
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
        for player_name, turn_metric_bundle in (turn_metrics or {}).items():
            for metric_name, value in turn_metric_bundle.items():
                if value is not None:
                    per_player[player_name][f"turn_metric_{metric_name}"].append(value)
        for player_name, usage_bundle in (usage_metrics or {}).items():
            input_tokens = _normalize_token_count(usage_bundle.get("input_tokens"))
            output_tokens = _normalize_token_count(usage_bundle.get("output_tokens"))
            reasoning_tokens = _normalize_token_count(
                usage_bundle.get("reasoning_tokens")
            )
            estimated_cost_usd = float(usage_bundle.get("estimated_total_cost_usd") or 0.0)

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_reasoning_tokens += reasoning_tokens
            total_estimated_cost_usd += estimated_cost_usd

            per_player[player_name]["usage_input_tokens"].append(input_tokens)
            per_player[player_name]["usage_output_tokens"].append(output_tokens)
            per_player[player_name]["usage_reasoning_tokens"].append(reasoning_tokens)
            per_player[player_name]["usage_estimated_cost_usd"].append(
                estimated_cost_usd
            )

            for missing_model in usage_bundle.get("missing_pricing_models", []):
                per_player_missing_pricing[player_name].add(missing_model)
                summary_missing_pricing_models.add(missing_model)

            for client_bundle in usage_bundle.get("by_client", []):
                client_key = (
                    f"{client_bundle.get('provider')}:{client_bundle.get('model')}:"
                    f"{client_bundle.get('client_role') or 'unknown'}"
                )
                aggregate_bundle = per_player_usage_breakdown[player_name].setdefault(
                    client_key,
                    {
                        "provider": client_bundle.get("provider"),
                        "model": client_bundle.get("model"),
                        "client_role": client_bundle.get("client_role"),
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "cached_input_tokens": 0,
                        "reasoning_tokens": 0,
                        "interaction_count": 0,
                        "estimated_total_cost_usd": 0.0,
                    },
                )
                for metric_name in (
                    "input_tokens",
                    "output_tokens",
                    "total_tokens",
                    "cached_input_tokens",
                    "reasoning_tokens",
                    "interaction_count",
                ):
                    aggregate_bundle[metric_name] += _normalize_token_count(
                        client_bundle.get(metric_name)
                    )
                aggregate_bundle["estimated_total_cost_usd"] += float(
                    client_bundle.get("estimated_total_cost_usd") or 0.0
                )
        for player_name, error_bundle in result.get("error_counts", {}).items():
            for error_name, count in error_bundle.items():
                per_player[player_name][f"error_{error_name}"].append(count)

    players_summary = {}
    for player_name, metrics in per_player.items():
        total_player_input_tokens = sum(metrics["usage_input_tokens"])
        total_player_output_tokens = sum(metrics["usage_output_tokens"])
        total_player_reasoning_tokens = sum(metrics["usage_reasoning_tokens"])
        total_player_cost_usd = round(sum(metrics["usage_estimated_cost_usd"]), 8)
        wins = win_counts.get(player_name, 0)
        total_successful_attacks = sum(metrics["turn_metric_total_successful_attacks"])
        cost_per_win = None
        wins_per_usd = None
        successful_attacks_per_usd = None
        if total_player_cost_usd > 0:
            wins_per_usd = round(wins / total_player_cost_usd, 6)
            successful_attacks_per_usd = round(
                total_successful_attacks / total_player_cost_usd,
                3,
            )
            if wins > 0:
                cost_per_win = round(total_player_cost_usd / wins, 6)

        players_summary[player_name] = {
            "wins": wins,
            "mean_final_territories": _rounded_mean(metrics["territories"]),
            "mean_turn_time_seconds": _rounded_mean(metrics["turn_times"]),
            "mean_strategic_score": _rounded_mean(metrics["strategic_scores"]),
            "mean_fallback_count": _rounded_mean(metrics["fallback_counts"]),
            "total_input_tokens": total_player_input_tokens,
            "total_output_tokens": total_player_output_tokens,
            "total_reasoning_tokens": total_player_reasoning_tokens,
            "mean_input_tokens_per_game": _rounded_mean(
                metrics["usage_input_tokens"],
            ),
            "mean_output_tokens_per_game": _rounded_mean(
                metrics["usage_output_tokens"],
            ),
            "mean_reasoning_tokens_per_game": _rounded_mean(
                metrics["usage_reasoning_tokens"],
            ),
            "estimated_total_cost_usd": total_player_cost_usd,
            "mean_cost_per_game_usd": _rounded_mean(
                metrics["usage_estimated_cost_usd"],
                digits=6,
            ),
            "estimated_cost_per_win_usd": cost_per_win,
            "wins_per_usd": wins_per_usd,
            "mean_successful_attacks_per_turn": _rounded_mean(
                metrics["turn_metric_average_successful_attacks_per_turn"],
                digits=3,
            ),
            "mean_successful_attacks_per_attacking_turn": _rounded_mean(
                metrics["turn_metric_average_successful_attacks_per_attacking_turn"],
                digits=3,
            ),
            "mean_attack_turn_rate": _rounded_mean(
                metrics["turn_metric_attack_turn_rate"],
                digits=3,
            ),
            "mean_territory_delta_per_turn": _rounded_mean(
                metrics["turn_metric_average_territory_delta_per_turn"],
                digits=3,
            ),
            "mean_timed_out_turn_count": _rounded_mean(
                metrics["turn_metric_timed_out_turn_count"],
            ),
            "total_successful_attacks": total_successful_attacks,
            "total_failed_attacks": sum(metrics["turn_metric_total_failed_attacks"]),
            "successful_attacks_per_usd": successful_attacks_per_usd,
            "mean_placement_errors": _rounded_mean(metrics["error_placement"]),
            "mean_attack_errors": _rounded_mean(metrics["error_attack"]),
            "mean_fortify_errors": _rounded_mean(metrics["error_fortify"]),
            "mean_card_trade_errors": _rounded_mean(metrics["error_card_trade"]),
            "mean_formatting_errors": _rounded_mean(metrics["error_formatting"]),
            "cost_breakdown_by_client": sorted(
                (
                    {
                        **client_bundle,
                        "estimated_total_cost_usd": round(
                            client_bundle["estimated_total_cost_usd"], 8
                        ),
                    }
                    for client_bundle in per_player_usage_breakdown[
                        player_name
                    ].values()
                ),
                key=lambda item: (
                    -(item["estimated_total_cost_usd"] or 0.0),
                    item.get("provider") or "",
                    item.get("model") or "",
                    item.get("client_role") or "",
                ),
            ),
            "missing_pricing_models": sorted(per_player_missing_pricing[player_name]),
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
        "pricing_snapshot_id": PRICING_SNAPSHOT_ID,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_reasoning_tokens": total_reasoning_tokens,
        "total_estimated_cost_usd": round(total_estimated_cost_usd, 8),
        "missing_pricing_models": sorted(summary_missing_pricing_models),
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
        f"- Pricing snapshot: {summary.get('pricing_snapshot_id')}",
        f"- Total input tokens: {summary.get('total_input_tokens')}",
        f"- Total output tokens: {summary.get('total_output_tokens')}",
        f"- Total reasoning tokens: {summary.get('total_reasoning_tokens')}",
        f"- Total estimated cost USD: {summary.get('total_estimated_cost_usd')}",
        "",
        "## Win Counts",
    ]
    if summary.get("missing_pricing_models"):
        lines.append(
            "- Missing pricing models: "
            + ", ".join(summary["missing_pricing_models"])
        )
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
        lines.append(f"- Total input tokens: {metrics['total_input_tokens']}")
        lines.append(f"- Total output tokens: {metrics['total_output_tokens']}")
        lines.append(f"- Total reasoning tokens: {metrics['total_reasoning_tokens']}")
        lines.append(f"- Mean input tokens per game: {metrics['mean_input_tokens_per_game']}")
        lines.append(
            f"- Mean output tokens per game: {metrics['mean_output_tokens_per_game']}"
        )
        lines.append(
            f"- Mean reasoning tokens per game: {metrics['mean_reasoning_tokens_per_game']}"
        )
        lines.append(f"- Estimated total cost USD: {metrics['estimated_total_cost_usd']}")
        lines.append(f"- Mean cost per game USD: {metrics['mean_cost_per_game_usd']}")
        lines.append(
            f"- Estimated cost per win USD: {metrics['estimated_cost_per_win_usd']}"
        )
        lines.append(f"- Wins per USD: {metrics['wins_per_usd']}")
        lines.append(
            f"- Mean successful attacks per turn: "
            f"{metrics['mean_successful_attacks_per_turn']}"
        )
        lines.append(
            f"- Mean successful attacks per attacking turn: "
            f"{metrics['mean_successful_attacks_per_attacking_turn']}"
        )
        lines.append(f"- Mean attack-turn rate: {metrics['mean_attack_turn_rate']}")
        lines.append(
            f"- Mean territory delta per turn: "
            f"{metrics['mean_territory_delta_per_turn']}"
        )
        lines.append(
            f"- Mean timed-out turns per game: "
            f"{metrics['mean_timed_out_turn_count']}"
        )
        lines.append(
            f"- Total successful attacks: {metrics['total_successful_attacks']}"
        )
        lines.append(f"- Total failed attacks: {metrics['total_failed_attacks']}")
        lines.append(
            f"- Successful attacks per USD: {metrics['successful_attacks_per_usd']}"
        )
        lines.append(f"- Mean placement errors: {metrics['mean_placement_errors']}")
        lines.append(f"- Mean attack errors: {metrics['mean_attack_errors']}")
        lines.append(f"- Mean fortify errors: {metrics['mean_fortify_errors']}")
        lines.append(f"- Mean card-trade errors: {metrics['mean_card_trade_errors']}")
        lines.append(f"- Mean formatting errors: {metrics['mean_formatting_errors']}")
        if metrics["missing_pricing_models"]:
            lines.append(
                "- Missing pricing models: "
                + ", ".join(metrics["missing_pricing_models"])
            )
        for client_bundle in metrics["cost_breakdown_by_client"]:
            lines.append(
                "- Cost breakdown: "
                f"{client_bundle['provider']}:{client_bundle['model']}"
                f" [{client_bundle.get('client_role') or 'unknown'}] "
                f"cost=${client_bundle['estimated_total_cost_usd']:.6f}, "
                f"in={client_bundle['input_tokens']}, "
                f"out={client_bundle['output_tokens']}, "
                f"reasoning={client_bundle['reasoning_tokens']}"
            )
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
