from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Set

from risk_game.game_constants import CONTINENT_BONUSES, TERRITORIES


TERRITORY_TO_CONTINENT = {
    territory.lower(): continent
    for continent, (territories, _) in CONTINENT_BONUSES.items()
    for territory in territories
}

PLAN_ATTACK_WORDS = {
    "attack",
    "pressure",
    "push",
    "conquer",
    "take",
    "eliminate",
}
PLAN_REINFORCE_WORDS = {
    "reinforce",
    "stack",
    "build",
    "placement",
    "front",
    "border",
}
PLAN_FORTIFY_WORDS = {"fortify", "shift", "move", "reserve", "redistribute"}
PLAN_HOLD_WORDS = {"hold", "defend", "consolidate", "avoid", "skip", "stabilize"}


def _clamp(score: int | float, minimum: int = 0, maximum: int = 5) -> int:
    return max(minimum, min(maximum, int(round(score))))


def _extract_references(plan_text: str) -> Dict[str, List[str]]:
    normalized = plan_text.lower()
    territories = [
        territory
        for territory in TERRITORIES
        if territory.lower() in normalized
    ]
    continents = [
        continent
        for continent in CONTINENT_BONUSES
        if continent.lower() in normalized
    ]
    return {"territories": territories, "continents": continents}


def _collect_action_territories(turn_summary: Dict[str, Any]) -> Set[str]:
    action_territories: Set[str] = set()
    for event in turn_summary.get("events", []):
        for move in event.get("moves", []):
            territory_name = move.get("territory_name")
            if territory_name and territory_name != "Blank":
                action_territories.add(territory_name)

        for field in ("from_territory", "to_territory", "target_territory"):
            territory_name = event.get(field)
            if territory_name and territory_name != "Blank":
                action_territories.add(territory_name)

    return action_territories


def _territories_to_continents(territories: Iterable[str]) -> Set[str]:
    continents = set()
    for territory in territories:
        continent = TERRITORY_TO_CONTINENT.get(territory.lower())
        if continent:
            continents.add(continent)
    return continents


def _contains_any_word(plan_text: str, words: Set[str]) -> bool:
    normalized = plan_text.lower()
    return any(re.search(rf"\b{re.escape(word)}\b", normalized) for word in words)


def score_plan_concreteness(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    plan_text = (turn_summary.get("plan", {}).get("text") or "").strip()
    if not plan_text or plan_text == "No explicit turn plan.":
        return {
            "score": 0,
            "notes": ["No explicit pre-turn plan was recorded."],
        }

    words = re.findall(r"\b[\w'-]+\b", plan_text)
    strategic_flags = sum(
        [
            _contains_any_word(plan_text, PLAN_ATTACK_WORDS),
            _contains_any_word(plan_text, PLAN_REINFORCE_WORDS),
            _contains_any_word(plan_text, PLAN_FORTIFY_WORDS),
            _contains_any_word(plan_text, PLAN_HOLD_WORDS),
        ]
    )
    references = _extract_references(plan_text)

    score = 1
    if len(words) >= 4:
        score += 1
    if len(words) >= 8:
        score += 1
    if strategic_flags >= 2:
        score += 1
    if references["territories"] or references["continents"]:
        score += 1

    notes = [f"Plan length: {len(words)} words."]
    if strategic_flags:
        notes.append(f"Strategic intent markers: {strategic_flags}.")
    if references["territories"]:
        notes.append(
            "References territories: " + ", ".join(references["territories"][:3]) + "."
        )
    if references["continents"]:
        notes.append(
            "References continents: " + ", ".join(references["continents"][:3]) + "."
        )

    return {"score": _clamp(score), "notes": notes}


def score_action_validity(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    derived = turn_summary["derived"]
    invalid_actions = int(derived["invalid_action_count"])
    fallback_count = int(derived["random_fallback_count"])

    score = 5 - invalid_actions - (2 * fallback_count)
    notes = [
        f"Invalid actions: {invalid_actions}.",
        f"Random fallbacks: {fallback_count}.",
    ]
    if invalid_actions == 0 and fallback_count == 0:
        notes.append("Execution stayed within legal move space.")

    return {"score": _clamp(score), "notes": notes}


def score_plan_alignment(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    plan_text = (turn_summary.get("plan", {}).get("text") or "").strip()
    if not plan_text or plan_text == "No explicit turn plan.":
        return {
            "score": 0,
            "notes": ["Cannot score alignment without a recorded plan."],
        }

    derived = turn_summary["derived"]
    actions = turn_summary.get("events", [])
    action_territories = _collect_action_territories(turn_summary)
    action_continents = _territories_to_continents(action_territories)

    planned_attack = _contains_any_word(plan_text, PLAN_ATTACK_WORDS)
    planned_fortify = _contains_any_word(plan_text, PLAN_FORTIFY_WORDS)
    planned_hold = _contains_any_word(plan_text, PLAN_HOLD_WORDS)

    attacked = any(
        event.get("phase") == "attack"
        and event.get("outcome") in {"win", "lose"}
        for event in actions
    )
    fortified = any(
        event.get("phase") == "fortify" and event.get("outcome") == "applied"
        for event in actions
    )
    skipped_attack = bool(derived["skipped_attack"])

    plan_targets = _extract_references(plan_text)
    territory_match = bool(set(plan_targets["territories"]) & action_territories)
    continent_match = bool(
        set(plan_targets["continents"])
        & (
            action_continents
            | set(derived["new_continents"])
            | set(derived["lost_continents"])
        )
    )

    intended_axes = 0
    matched_axes = 0
    notes: List[str] = []

    if planned_attack:
        intended_axes += 1
        if attacked:
            matched_axes += 1
            notes.append("Attack intent matched actual attacks.")
        else:
            notes.append("Attack intent was not reflected in executed attacks.")

    if planned_fortify:
        intended_axes += 1
        if fortified:
            matched_axes += 1
            notes.append("Fortify intent matched actual fortification.")
        else:
            notes.append("Fortify intent was not reflected in executed fortification.")

    if planned_hold:
        intended_axes += 1
        if skipped_attack:
            matched_axes += 1
            notes.append("Hold/defend intent matched restrained attack behavior.")
        else:
            notes.append("Hold/defend intent did not match attack behavior.")

    if intended_axes == 0:
        base_score = 2
        notes.append("Plan did not include a clearly classifiable intent axis.")
    else:
        base_score = 1 + round((matched_axes / intended_axes) * 3)

    if territory_match or continent_match:
        base_score += 1
        if territory_match:
            notes.append("Plan referenced territories that appeared in executed moves.")
        if continent_match:
            notes.append("Plan referenced continents that aligned with action geography.")

    return {"score": _clamp(base_score), "notes": notes}


def score_tactical_efficiency(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    derived = turn_summary["derived"]
    successful_attacks = int(derived["successful_attack_count"])
    failed_attacks = int(derived["failed_attack_count"])
    territory_delta = int(derived["territory_delta"])
    troop_delta = int(derived["troop_delta"])
    total_resolved_attacks = successful_attacks + failed_attacks

    if total_resolved_attacks == 0:
        score = 3 if derived["skipped_attack"] else 2
        notes = [
            "No resolved attacks this turn.",
            (
                "Attack phase ended without forcing low-confidence fights."
                if derived["skipped_attack"]
                else "No clear tactical pressure was converted into attacks."
            ),
        ]
        return {"score": score, "notes": notes}

    win_rate = successful_attacks / total_resolved_attacks
    if win_rate >= 0.75:
        score = 5
    elif win_rate >= 0.5:
        score = 4
    elif successful_attacks > 0:
        score = 3
    else:
        score = 1

    if territory_delta > 0 and score < 5:
        score += 1
    if troop_delta < 0 and territory_delta <= 0:
        score -= 1

    notes = [
        f"Resolved attacks: {total_resolved_attacks}.",
        f"Attack win rate: {win_rate:.0%}.",
    ]
    if territory_delta > 0:
        notes.append("Attacks translated into net territorial gain.")
    if troop_delta < 0 and territory_delta <= 0:
        notes.append("Troops were spent without improving board position.")

    return {"score": _clamp(score), "notes": notes}


def score_positional_outcome(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    pre_state = turn_summary["pre_turn"]["player_state"]
    post_state = turn_summary["post_turn"]["player_state"]
    derived = turn_summary["derived"]
    border_pressure_delta = (
        int(post_state["border_pressure"]) - int(pre_state["border_pressure"])
    )

    score = 2
    notes = [
        (
            f"Territories: {pre_state['territories']} -> {post_state['territories']} "
            f"({derived['territory_delta']:+d})."
        ),
        (
            f"Distance to win: {pre_state['territories_to_win']} -> "
            f"{post_state['territories_to_win']}."
        ),
    ]

    if derived["territory_delta"] > 0:
        score += 1
    if derived["territory_delta"] >= 3:
        score += 1
    if derived["cards_delta"] > 0:
        score += 1
        notes.append("Turn ended with a positive card swing.")
    if derived["new_continents"]:
        score += 1
        notes.append(
            "Gained continents: " + ", ".join(derived["new_continents"]) + "."
        )
    if post_state["territories_to_win"] < pre_state["territories_to_win"]:
        score += 1
    if derived["lost_continents"]:
        score -= 1
        notes.append(
            "Lost continents: " + ", ".join(derived["lost_continents"]) + "."
        )
    if derived["territory_delta"] < 0:
        score -= 1
    if border_pressure_delta >= 3 and derived["territory_delta"] <= 0:
        score -= 1
        notes.append(
            f"Border pressure increased by {border_pressure_delta} without territorial gain."
        )

    return {"score": _clamp(score), "notes": notes}


def score_turn_summary(turn_summary: Dict[str, Any]) -> Dict[str, Any]:
    dimensions = {
        "plan_concreteness": score_plan_concreteness(turn_summary),
        "action_validity": score_action_validity(turn_summary),
        "plan_alignment": score_plan_alignment(turn_summary),
        "tactical_efficiency": score_tactical_efficiency(turn_summary),
        "positional_outcome": score_positional_outcome(turn_summary),
    }

    overall_score = round(
        sum(dimension["score"] for dimension in dimensions.values())
        / len(dimensions),
        2,
    )

    if overall_score >= 4.2:
        band = "strong"
    elif overall_score >= 3.0:
        band = "mixed"
    else:
        band = "weak"

    strongest_dimension = max(dimensions.items(), key=lambda item: item[1]["score"])[0]
    weakest_dimension = min(dimensions.items(), key=lambda item: item[1]["score"])[0]

    summary = (
        f"{band.title()} turn. Strongest dimension: {strongest_dimension}. "
        f"Weakest dimension: {weakest_dimension}."
    )

    return {
        "overall_score": overall_score,
        "band": band,
        "dimensions": dimensions,
        "summary": summary,
    }
