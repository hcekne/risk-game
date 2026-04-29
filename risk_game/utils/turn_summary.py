from __future__ import annotations

from typing import Any, Dict, List

from risk_game.game_constants import CONTINENT_BONUSES


def build_player_model_info(player: "PlayerAgent") -> Dict[str, Any]:
    llm_client = player.llm_client
    info: Dict[str, Any] = {
        "name": player.name,
        "provider": getattr(llm_client, "provider_name", None),
        "model": getattr(llm_client, "model_type", None),
    }

    if hasattr(llm_client, "reasoning_effort"):
        info["reasoning_effort"] = getattr(llm_client, "reasoning_effort")
    if hasattr(llm_client, "verbosity"):
        info["verbosity"] = getattr(llm_client, "verbosity")

    return info


def snapshot_player_state(
    game_state: "GameState",
    player_name: str,
    *,
    border_limit: int = 5,
    reserve_limit: int = 5,
) -> Dict[str, Any]:
    status = game_state.get_player_status(player_name)
    continent_bonus = sum(
        CONTINENT_BONUSES[continent][1] for continent in status["continents"]
    )
    border_territories = game_state.get_border_territories(player_name)
    interior_reserves = game_state.get_interior_reserves(player_name)

    return {
        "territories": int(status["territories"]),
        "troops": int(status["troops"]),
        "capital": status["capital"],
        "continents": list(status["continents"]),
        "continent_bonus": int(continent_bonus),
        "territories_to_win": int(
            max(game_state.territories_required_to_win - status["territories"], 0)
        ),
        "border_count": len(border_territories),
        "border_pressure": int(
            sum(len(enemy_neighbors) for _, _, enemy_neighbors in border_territories)
        ),
        "border_territories": [
            {
                "territory": territory,
                "troops": int(troops),
                "enemy_neighbors": [
                    {
                        "territory": neighbor,
                        "owner": owner,
                        "troops": int(enemy_troops),
                    }
                    for neighbor, owner, enemy_troops in enemy_neighbors
                ],
            }
            for territory, troops, enemy_neighbors in border_territories[:border_limit]
        ],
        "interior_reserves": [
            {"territory": territory, "movable_troops": int(movable_troops)}
            for territory, movable_troops in interior_reserves[:reserve_limit]
        ],
        "top_continent_progress": [
            {
                "continent": continent,
                "controlled": int(controlled),
                "total": int(total),
                "bonus": int(bonus),
            }
            for continent, controlled, total, bonus in game_state.get_continent_progress(
                player_name
            )[:3]
        ],
    }


def snapshot_all_players(game_state: "GameState") -> Dict[str, Dict[str, Any]]:
    return {
        player_name: snapshot_player_state(
            game_state,
            player_name,
            border_limit=3,
            reserve_limit=3,
        )
        for player_name in game_state.territories_df.columns[1:]
    }


def build_turn_outcome(
    pre_turn_state: Dict[str, Any],
    post_turn_state: Dict[str, Any],
    events: List[Dict[str, Any]],
    *,
    cards_before: int,
    cards_after: int,
    turn_time_seconds: float,
) -> Dict[str, Any]:
    pre_continents = set(pre_turn_state["continents"])
    post_continents = set(post_turn_state["continents"])
    attack_events = [event for event in events if event.get("phase") == "attack"]

    return {
        "territory_delta": int(
            post_turn_state["territories"] - pre_turn_state["territories"]
        ),
        "troop_delta": int(post_turn_state["troops"] - pre_turn_state["troops"]),
        "cards_delta": int(cards_after - cards_before),
        "new_continents": sorted(post_continents - pre_continents),
        "lost_continents": sorted(pre_continents - post_continents),
        "invalid_action_count": sum(
            1 for event in events if event.get("valid") is False
        ),
        "random_fallback_count": sum(
            1 for event in events if event.get("fallback") is True
        ),
        "successful_attack_count": sum(
            1 for event in attack_events if event.get("outcome") == "win"
        ),
        "failed_attack_count": sum(
            1 for event in attack_events if event.get("outcome") == "lose"
        ),
        "skipped_attack": any(
            event.get("outcome") == "no_attack" for event in attack_events
        ),
        "completed_card_trades": sum(
            1
            for event in events
            if event.get("phase") in {"mandatory_card_trade", "optional_card_trade"}
            and event.get("outcome") == "trade_completed"
        ),
        "turn_time_seconds": round(float(turn_time_seconds), 2),
    }


def render_turn_summary_markdown(turn_summary: Dict[str, Any]) -> str:
    player_name = turn_summary["player"]["name"]
    pre_state = turn_summary["pre_turn"]["player_state"]
    post_state = turn_summary["post_turn"]["player_state"]
    derived = turn_summary["derived"]
    plan_text = turn_summary.get("plan", {}).get("text") or "No explicit turn plan."

    lines = [
        (
            f"### Round {turn_summary['game_round']} · "
            f"Turn {turn_summary['turn_number']} · {player_name}"
        ),
        f"Plan: {plan_text}",
        (
            "Result: "
            f"territories {pre_state['territories']} -> {post_state['territories']} "
            f"({derived['territory_delta']:+d}), "
            f"troops {pre_state['troops']} -> {post_state['troops']} "
            f"({derived['troop_delta']:+d}), "
            f"cards {turn_summary['pre_turn']['cards']} -> {turn_summary['post_turn']['cards']} "
            f"({derived['cards_delta']:+d}), "
            f"time {derived['turn_time_seconds']:.2f}s"
        ),
    ]

    if derived["new_continents"] or derived["lost_continents"]:
        continent_parts = []
        if derived["new_continents"]:
            continent_parts.append(
                "gained " + ", ".join(derived["new_continents"])
            )
        if derived["lost_continents"]:
            continent_parts.append("lost " + ", ".join(derived["lost_continents"]))
        lines.append("Continents: " + "; ".join(continent_parts))

    lines.append("Actions:")
    if not turn_summary["events"]:
        lines.append("- none recorded")
        return "\n".join(lines)

    for event in turn_summary["events"]:
        phase = event["phase"]
        outcome = event.get("outcome")
        reason = event.get("reasoning") or "no reasoning"
        error = event.get("error")

        if phase in {"troop_placement", "initial_troop_placement"}:
            move_text = ", ".join(
                f"{move['territory_name']}+{move['num_troops']}"
                for move in event.get("moves", [])
            )
        elif phase == "attack":
            move_text = (
                f"{event.get('from_territory')} -> {event.get('target_territory')} "
                f"with {event.get('attack_troops')}"
            )
        elif phase == "fortify":
            move_text = (
                f"{event.get('from_territory')} -> {event.get('to_territory')} "
                f"with {event.get('moved_troops')}"
            )
        else:
            move_text = str(event.get("selected_cards"))

        line = (
            f"- {phase}: attempt {event.get('attempt', 1)} "
            f"{'valid' if event.get('valid') else 'invalid'}"
        )
        if outcome:
            line += f", outcome={outcome}"
        if move_text and move_text != "None":
            line += f", move={move_text}"
        line += f", reason={reason}"
        if error:
            line += f", error={error}"
        lines.append(line)

    return "\n".join(lines)
