import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from risk_game.game_config import GameConfig
from risk_game.game_constants import TERRITORIES
from risk_game.game_master import GameMaster
from risk_game.game_state import GameState
from risk_game.llm_clients.llm_base import LLMClient
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.player_agent import PlayerAgent
from risk_game.rules import Rules


class DummyLLMClient(LLMClient):
    def __init__(self) -> None:
        super().__init__(provider_name="dummy", model_type="dummy")

    def get_chat_completion(self, messages, **kwargs) -> str:
        raise RuntimeError("Dummy probe client should never be called.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a deterministic breakthrough scenario against a live model to "
            "test whether it can identify and execute a fast attack chain."
        )
    )
    parser.add_argument("--provider", default="OpenAI")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument(
        "--variants",
        nargs="+",
        default=["full", "bare"],
        help=(
            "Prompt variants / architectures to probe: "
            "full, no_time_budget, no_final_check, bare, "
            "minimal_baseline, system_prompt_only, system_plus_execution_handoff, full_live"
        ),
    )
    parser.add_argument("--turn-time-limit-seconds", type=int, default=300)
    parser.add_argument("--placement-time-limit-seconds", type=int, default=25)
    parser.add_argument("--max-attacks", type=int, default=12)
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path. Defaults under game_results/model_probes/.",
    )
    return parser.parse_args()


def set_territory_owner(
    game_state: GameState, territory: str, player_name: str, troops: int
) -> None:
    row_mask = game_state.territories_df["Territory"] == territory
    player_columns = list(game_state.territories_df.columns[1:])
    game_state.territories_df.loc[row_mask, player_columns] = 0
    game_state.territories_df.loc[row_mask, player_name] = troops


def build_probe_master(
    *,
    provider: str,
    model: str,
    reasoning_effort: str,
    turn_time_limit_seconds: int,
    placement_time_limit_seconds: int,
) -> tuple[GameMaster, PlayerAgent]:
    config = GameConfig(
        progressive=True,
        capitals=False,
        max_rounds=15,
        turn_time_limit_seconds=turn_time_limit_seconds,
        placement_time_limit_seconds=placement_time_limit_seconds,
        placement_reasoning_effort="medium",
        planning_reasoning_effort=reasoning_effort,
        attack_reasoning_effort=reasoning_effort,
        fortify_reasoning_effort="medium",
        card_trade_reasoning_effort="medium",
    )
    rules = Rules(config)
    master = GameMaster(rules)

    probe_player = PlayerAgent(
        "Probe",
        create_llm_client(
            provider,
            model,
            reasoning_effort=reasoning_effort,
            verbosity="low",
        ),
    )
    opponent_na = PlayerAgent("NorthAmerica", DummyLLMClient())
    opponent_eu = PlayerAgent("Europe", DummyLLMClient())
    opponent_asia = PlayerAgent("Asia", DummyLLMClient())

    master.players = [probe_player, opponent_na, opponent_eu, opponent_asia]
    master.active_players = master.players.copy()
    master.dead_players = []
    master.player_cards = {player.name: [] for player in master.players}
    master.game_state = GameState(master.players, rules)
    master.phase = 2
    master.game_round = 1

    for player in master.players:
        master._apply_runtime_settings_to_player(player)

    setup_breakthrough_scenario(master.game_state, probe_player.name)
    return master, probe_player


def setup_breakthrough_scenario(game_state: GameState, probe_name: str) -> None:
    owner_cycle = ["NorthAmerica", "Europe", "Asia"]
    for index, territory in enumerate(TERRITORIES):
        set_territory_owner(game_state, territory, owner_cycle[index % 3], 1)

    probe_territories = {
        "Iceland": 30,
        # Block Iceland's side exits without creating another viable front.
        "Great Britain": 1,
        "Scandinavia": 1,
        # Give the probe a few harmless holdings elsewhere so the player is not
        # trivially one-territory, but avoid any other attractive attack fronts.
        "Argentina": 1,
        "Madagascar": 1,
        "Indonesia": 1,
    }
    for territory, troops in probe_territories.items():
        set_territory_owner(game_state, territory, probe_name, troops)

    # Make the North America line the only clearly favorable breakthrough.
    # The intended sequence is:
    # Iceland -> Greenland -> Quebec/Ontario/Northwest Territory -> deeper NA
    north_america_chain = {
        "Greenland": ("NorthAmerica", 1),
        "Quebec": ("NorthAmerica", 1),
        "Ontario": ("NorthAmerica", 1),
        "Eastern United States": ("NorthAmerica", 1),
        "Western United States": ("NorthAmerica", 1),
        "Alberta": ("NorthAmerica", 1),
        "Northwest Territory": ("NorthAmerica", 1),
        "Central America": ("NorthAmerica", 1),
        "Alaska": ("NorthAmerica", 8),
    }
    for territory, (owner, troops) in north_america_chain.items():
        set_territory_owner(game_state, territory, owner, troops)

    # Keep the downstream North America chain weak so the best move is to break
    # quickly and keep pressing while time remains.
    set_territory_owner(game_state, "Northern Europe", "Europe", 9)
    set_territory_owner(game_state, "Western Europe", "Europe", 9)
    set_territory_owner(game_state, "Ukraine", "Asia", 9)
    set_territory_owner(game_state, "North Africa", "Europe", 9)


def apply_variant(player: PlayerAgent, variant: str) -> None:
    player.llm_client.set_system_prompt_profile("timed_risk_live")
    player.prompt_include_time_budget = True
    player.prompt_repeat_key_points = True
    player.prompt_use_attack_plan_handoff = True

    if variant in {"full", "full_live"}:
        return
    if variant == "bare":
        player.prompt_include_time_budget = False
        player.prompt_repeat_key_points = False
        return
    if variant == "no_time_budget":
        player.prompt_include_time_budget = False
        return
    if variant == "no_final_check":
        player.prompt_repeat_key_points = False
        return
    if variant == "minimal_baseline":
        player.llm_client.set_system_prompt_profile("minimal")
        player.prompt_include_time_budget = False
        player.prompt_repeat_key_points = False
        player.prompt_use_attack_plan_handoff = False
        return
    if variant == "system_prompt_only":
        player.prompt_include_time_budget = False
        player.prompt_repeat_key_points = False
        player.prompt_use_attack_plan_handoff = False
        return
    if variant == "system_plus_execution_handoff":
        player.prompt_include_time_budget = False
        player.prompt_repeat_key_points = False
        player.prompt_use_attack_plan_handoff = True
        return
    raise ValueError(
        f"Unknown probe variant '{variant}'."
    )


def deterministic_attack_resolution(
    game_state: GameState,
    player: PlayerAgent,
    move: List[Dict[str, int]],
    from_territory: str,
) -> tuple[str, str]:
    territory = move[0].get("territory_name")
    num_troops = move[0].get("num_troops")
    if territory == "Blank" or num_troops == 0:
        return ("no_attack", "_")

    defender_name, defender_troops = game_state.get_territory_control(territory)
    game_state.update_troops(player.name, from_territory, -num_troops)
    remaining_troops = max(num_troops - min(defender_troops, num_troops - 1), 1)
    game_state.update_troops(defender_name, territory, 0, set_troops=True)
    game_state.update_troops(player.name, territory, remaining_troops, set_troops=True)
    return ("win", defender_name)


def run_variant(
    *,
    provider: str,
    model: str,
    reasoning_effort: str,
    variant: str,
    turn_time_limit_seconds: int,
    placement_time_limit_seconds: int,
    max_attacks: int,
) -> Dict[str, Any]:
    master, player = build_probe_master(
        provider=provider,
        model=model,
        reasoning_effort=reasoning_effort,
        turn_time_limit_seconds=turn_time_limit_seconds,
        placement_time_limit_seconds=placement_time_limit_seconds,
    )
    apply_variant(player, variant)

    north_america_targets = {
        "Greenland",
        "Quebec",
        "Ontario",
        "Eastern United States",
        "Western United States",
        "Alberta",
        "Northwest Territory",
        "Central America",
        "Alaska",
    }

    original_attack_update = master.game_state.update_game_state_for_attack_move
    master.game_state.update_game_state_for_attack_move = (
        lambda player_obj, move, from_territory: deterministic_attack_resolution(
            master.game_state, player_obj, move, from_territory
        )
    )

    started_at = time.time()
    player.set_interaction_context(game_round=1, turn_number=1, scope="turn")
    master._start_turn_trace(player)
    player.start_turn_timer(player.turn_time_limit_seconds)
    player.define_strategy_for_move(master.rules, master.game_state)
    master._capture_turn_plan(player)

    successful_attacks = 0
    attack_events: List[Dict[str, Any]] = []
    while successful_attacks < max_attacks and not player.turn_time_exhausted:
        previous_event_count = len(master.current_turn_trace["events"])
        successful_attacks, _ = master.ensure_valid_attack_move(player)
        new_events = master.current_turn_trace["events"][previous_event_count:]
        attack_events.extend(new_events)
        if not new_events:
            break
        if new_events[-1].get("outcome") == "no_attack":
            break
        if len(new_events) >= 3 and all(
            event.get("outcome") == "invalid" for event in new_events[-3:]
        ):
            break
        if player.turn_time_exhausted:
            break

    completed_trace = master._finalize_turn_trace(player, 1)
    player.clear_turn_timer()
    master.game_state.update_game_state_for_attack_move = original_attack_update
    elapsed_seconds = round(time.time() - started_at, 3)

    captured_targets = [
        territory
        for territory in north_america_targets
        if master.game_state.check_terr_control(player.name, territory)
    ]

    return {
        "variant": variant,
        "system_prompt_profile": getattr(player.llm_client, "system_prompt_profile", None),
        "turn_time_limit_seconds": turn_time_limit_seconds,
        "placement_time_limit_seconds": placement_time_limit_seconds,
        "elapsed_seconds": elapsed_seconds,
        "successful_attacks": successful_attacks,
        "turn_timed_out": player.turn_time_exhausted,
        "captured_north_america_targets": captured_targets,
        "captured_target_count": len(captured_targets),
        "reached_alaska_frontier": any(
            territory in captured_targets
            for territory in ("Northwest Territory", "Alberta", "Western United States")
        ),
        "controls_alaska": "Alaska" in captured_targets,
        "prompt_include_time_budget": player.prompt_include_time_budget,
        "prompt_repeat_key_points": player.prompt_repeat_key_points,
        "prompt_use_attack_plan_handoff": player.prompt_use_attack_plan_handoff,
        "plan": completed_trace.get("plan"),
        "events": completed_trace.get("events", []),
        "llm_decisions": completed_trace.get("llm_decisions", []),
    }


def main() -> None:
    args = parse_args()
    results = []
    for variant in args.variants:
        result = run_variant(
            provider=args.provider,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            variant=variant,
            turn_time_limit_seconds=args.turn_time_limit_seconds,
            placement_time_limit_seconds=args.placement_time_limit_seconds,
            max_attacks=args.max_attacks,
        )
        results.append(result)
        print(
            f"{variant}: captured={result['captured_target_count']} "
            f"successful_attacks={result['successful_attacks']} "
            f"timed_out={result['turn_timed_out']} "
            f"frontier={result['reached_alaska_frontier']} "
            f"alaska={result['controls_alaska']}"
        )

    output_path = args.output
    if output_path is None:
        output_dir = Path("game_results/model_probes/breakthrough_scenarios")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / (
            f"{args.model.replace('/', '_')}_{int(time.time())}.json"
        )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider": args.provider,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "turn_time_limit_seconds": args.turn_time_limit_seconds,
        "placement_time_limit_seconds": args.placement_time_limit_seconds,
        "variants": args.variants,
        "results": results,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Saved probe results to {output_path}")


if __name__ == "__main__":
    main()
