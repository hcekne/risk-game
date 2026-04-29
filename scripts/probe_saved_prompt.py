import argparse
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from risk_game.llm_clients.llm_base import LLMClient
from risk_game.llm_clients.llm_client import create_llm_client
from risk_game.llm_clients.openai_client import OpenAIClient
from risk_game.player_agent import PlayerAgent


class NoopLLMClient(LLMClient):
    def __init__(self) -> None:
        super().__init__(provider_name="noop", model_type="noop")

    def get_chat_completion(self, messages, **kwargs) -> str:
        raise RuntimeError("Noop client should not be called directly.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay a saved prompt JSON against one or more live models and "
            "report latency, parseability, and placement legality."
        )
    )
    parser.add_argument(
        "--prompt-json",
        required=True,
        help="Path to a saved llm_interactions/*.json prompt file.",
    )
    parser.add_argument(
        "--provider",
        default="OpenAI",
        help="Provider name passed to create_llm_client(). Default: OpenAI",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="Explicit model IDs to probe.",
    )
    parser.add_argument(
        "--reasoning-efforts",
        nargs="+",
        default=["low", "medium", "high"],
        help="Requested reasoning efforts to probe for each model.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Override timeout for each probe call. Defaults to the saved prompt timeout.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path. Defaults under game_results/model_probes/.",
    )
    return parser.parse_args()


def load_prompt_payload(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def extract_legal_placement_targets(prompt: str) -> List[str]:
    match = re.search(
        r"LEGAL PLACEMENT TARGETS:\n(.*?)\n\nOUTPUT FORMAT:",
        prompt,
        flags=re.DOTALL,
    )
    if not match:
        return []
    block = match.group(1)
    return sorted(set(re.findall(r"([A-Za-z][A-Za-z ',-]+?)\(\d+\)", block)))


def extract_expected_troops(phase: str, prompt: str) -> Optional[int]:
    if phase == "initial_troop_placement":
        return 1
    match = re.search(r"Distribute all (\d+) available troops", prompt)
    if match:
        return int(match.group(1))
    return None


def summarize_placement_result(
    phase: str,
    prompt: str,
    response_text: str,
) -> Dict[str, Any]:
    parser_agent = PlayerAgent("probe-parser", NoopLLMClient())
    moves, reasoning, from_territory = parser_agent.parse_response_text(response_text)
    legal_targets = extract_legal_placement_targets(prompt)
    expected_total = extract_expected_troops(phase, prompt)

    parsed_ok = all(move["territory_name"] is not None for move in moves)
    if not parsed_ok:
        return {
            "parsed_ok": False,
            "legal_targets": legal_targets,
            "expected_total": expected_total,
            "moves": moves,
            "reasoning": reasoning,
            "from_territory": from_territory,
            "all_targets_legal": False,
            "total_troops_matches": False,
            "looks_valid_for_engine": False,
        }

    move_targets = [move["territory_name"] for move in moves]
    total_troops = sum(move["num_troops"] for move in moves)
    all_targets_legal = (
        all(target in legal_targets for target in move_targets)
        if legal_targets
        else False
    )
    total_troops_matches = expected_total is not None and total_troops == expected_total
    looks_valid_for_engine = (
        all_targets_legal
        and total_troops_matches
        and all(target != "Blank" for target in move_targets)
    )

    return {
        "parsed_ok": True,
        "legal_targets": legal_targets,
        "expected_total": expected_total,
        "moves": moves,
        "reasoning": reasoning,
        "from_territory": from_territory,
        "all_targets_legal": all_targets_legal,
        "total_troops_matches": total_troops_matches,
        "looks_valid_for_engine": looks_valid_for_engine,
    }


def run_probe(
    *,
    provider: str,
    model_name: str,
    requested_reasoning_effort: Optional[str],
    prompt_payload: Dict[str, Any],
    timeout_seconds: Optional[float],
) -> Dict[str, Any]:
    phase = prompt_payload["phase"]
    prompt = prompt_payload["request"]["prompt"]
    saved_timeout = prompt_payload["request"].get("timeout_seconds")
    effective_timeout = saved_timeout if timeout_seconds is None else timeout_seconds
    constructor_reasoning_effort = requested_reasoning_effort

    if provider == "OpenAI":
        supported_efforts = OpenAIClient.supported_reasoning_efforts(model_name)
        if not supported_efforts:
            constructor_reasoning_effort = None
        elif requested_reasoning_effort not in supported_efforts:
            constructor_reasoning_effort = supported_efforts[0]

    client = create_llm_client(
        provider,
        model_name,
        reasoning_effort=constructor_reasoning_effort,
    )
    agent = PlayerAgent(model_name, client)
    started_at = time.time()
    raw_response = agent._send_prompt_with_logging(
        phase,
        prompt,
        reasoning_effort=requested_reasoning_effort,
        timeout_seconds=effective_timeout,
    )
    wall_clock_seconds = round(time.time() - started_at, 3)
    decision = agent.get_latest_turn_decision() or {}

    result: Dict[str, Any] = {
        "provider": provider,
        "model": model_name,
        "requested_reasoning_effort": requested_reasoning_effort,
        "constructor_reasoning_effort": constructor_reasoning_effort,
        "resolved_reasoning_effort": decision.get("reasoning_effort_override"),
        "phase": phase,
        "timeout_seconds": effective_timeout,
        "wall_clock_seconds": wall_clock_seconds,
        "used_fallback_response": decision.get("used_fallback_response"),
        "error": decision.get("error"),
        "error_type": decision.get("error_type"),
        "raw_response": raw_response,
    }

    if phase in {"initial_troop_placement", "troop_placement"}:
        result["placement_validation"] = summarize_placement_result(
            phase,
            prompt,
            raw_response,
        )

    return result


def main() -> None:
    args = parse_args()
    prompt_payload = load_prompt_payload(args.prompt_json)

    results = []
    for model_name in args.models:
        for reasoning_effort in args.reasoning_efforts:
            result = run_probe(
                provider=args.provider,
                model_name=model_name,
                requested_reasoning_effort=reasoning_effort,
                prompt_payload=prompt_payload,
                timeout_seconds=args.timeout_seconds,
            )
            results.append(result)
            status = "ok"
            placement_validation = result.get("placement_validation")
            if placement_validation is not None:
                status = (
                    "valid"
                    if placement_validation.get("looks_valid_for_engine")
                    else "invalid"
                )
            print(
                f"{model_name} requested={reasoning_effort} "
                f"resolved={result['resolved_reasoning_effort']} "
                f"time={result['wall_clock_seconds']:.3f}s "
                f"fallback={result['used_fallback_response']} "
                f"status={status}"
            )
            if result["error"]:
                print(f"  error: {result['error']}")
            print(f"  response: {result['raw_response'][:240].replace(chr(10), ' ')}")

    output_path = args.output
    if output_path is None:
        probe_dir = Path("game_results") / "model_probes"
        probe_dir.mkdir(parents=True, exist_ok=True)
        output_path = probe_dir / (
            f"{Path(args.prompt_json).stem}_{int(time.time())}.json"
        )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_json": args.prompt_json,
        "provider": args.provider,
        "models": args.models,
        "reasoning_efforts": args.reasoning_efforts,
        "results": results,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Saved probe results to {output_path}")


if __name__ == "__main__":
    main()
