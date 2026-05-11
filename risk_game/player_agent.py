import multiprocessing
import re
import signal
import time
import os
from datetime import datetime, timezone
from typing import Callable, Dict, Optional, List, Tuple
from risk_game.llm_clients.llm_base import LLMClient
from risk_game.game_constants import TERRITORIES
from risk_game.utils.provider_pause import detect_provider_pause_signal


_TERRITORY_NAME_LOOKUP = {
    territory.lower(): territory for territory in TERRITORIES
}
_TERRITORY_NAME_PATTERN = re.compile(
    "|".join(
        sorted(
            (re.escape(territory) for territory in TERRITORIES),
            key=len,
            reverse=True,
        )
    ),
    re.IGNORECASE,
)


def _llm_call_worker(
    llm_client: LLMClient,
    message_content: str,
    request_kwargs: Dict[str, object],
    response_queue: multiprocessing.Queue,
) -> None:
    try:
        llm_client.clear_last_response_metadata()
        if request_kwargs:
            try:
                response = llm_client.get_chat_completion(message_content, **request_kwargs)
            except TypeError:
                response = llm_client.get_chat_completion(message_content)
        else:
            response = llm_client.get_chat_completion(message_content)
        response_queue.put(("ok", response, llm_client.get_last_response_metadata()))
    except Exception as exc:
        response_queue.put(("error", type(exc).__name__, str(exc)))

class PlayerAgent:
    TURN_TIMEOUT_SAFETY_MARGIN_SECONDS = 5.0
    REASONING_EFFORT_ORDER = ("none", "minimal", "low", "medium", "high", "xhigh")

    def __init__(
        self,
        name: str,
        llm_client: LLMClient,
        planning_llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.name: str = name
        self.llm_client: LLMClient = llm_client
        self.planning_llm_client: Optional[LLMClient] = planning_llm_client
        self.include_reasoning: bool = True
        self.troops: int = 0
        self.turn_strategy: str = ""
        self.troop_placement_errors: int = 0
        self.return_formatting_errors: int = 0
        self.attack_errors: int = 0
        self.fortify_errors: int = 0
        self.card_trade_errors: int = 0
        self.capital: Optional[str] = None
        self.accumulated_turn_time : float = 0.0
        self.turn_decision_log: List[Dict[str, object]] = []
        self.turn_deadline: Optional[float] = None
        self.turn_time_exhausted: bool = False
        self.turn_time_limit_seconds: int = 90
        self.planning_time_limit_seconds: Optional[int] = None
        self.placement_time_limit_seconds: int = 15
        self.placement_reasoning_effort: Optional[str] = "low"
        self.planning_reasoning_effort: Optional[str] = "medium"
        self.attack_reasoning_effort: Optional[str] = "medium"
        self.fortify_reasoning_effort: Optional[str] = "medium"
        self.card_trade_reasoning_effort: Optional[str] = "low"
        self.runtime_overrides: Dict[str, object] = {}
        self.llm_interaction_logger: Optional[Callable[[Dict[str, object]], None]] = None
        self.current_game_round: int = 0
        self.current_turn_number: Optional[int] = None
        self.current_interaction_scope: str = "unscoped"
        self._interaction_sequence: int = 0
        self.prompt_include_time_budget: bool = False
        self.prompt_repeat_key_points: bool = False
        self.prompt_use_attack_plan_handoff: bool = True
        self.provider_pause_handler: Optional[Callable[[Dict[str, object]], None]] = None

    def __str__(self) -> str:
        return (f"Player: {self.name}\n"
                f"LLM Client: {self.llm_client}\n"
            f"Accumulated Turn Time: {self.accumulated_turn_time:.2f} seconds\n")
    
    def send_message(
        self,
        message_content: str,
        *,
        llm_client: Optional[LLMClient] = None,
        **kwargs,
    ) -> str:
        active_client = self.llm_client if llm_client is None else llm_client
        active_client.clear_last_response_metadata()
        if kwargs:
            try:
                return active_client.get_chat_completion(message_content, **kwargs)
            except TypeError:
                pass
        active_client.clear_last_response_metadata()
        return active_client.get_chat_completion(message_content)

    def _call_llm_with_timeout(
        self,
        message_content: str,
        *,
        llm_client: Optional[LLMClient] = None,
        timeout_seconds: Optional[float] = None,
        **kwargs,
    ) -> str:
        active_client = self.llm_client if llm_client is None else llm_client
        active_client.clear_last_response_metadata()
        if timeout_seconds is None:
            return self.send_message(message_content, llm_client=active_client, **kwargs)
        if timeout_seconds <= 0:
            raise TimeoutError("Wall-clock timeout expired before LLM call.")
        request_kwargs = dict(kwargs)
        request_kwargs["timeout_seconds"] = timeout_seconds
        if hasattr(os, "fork"):
            ctx = multiprocessing.get_context("fork")
            response_queue = ctx.Queue()
            process = ctx.Process(
                target=_llm_call_worker,
                args=(active_client, message_content, request_kwargs, response_queue),
            )
            process.start()
            process.join(timeout_seconds)
            if process.is_alive():
                process.terminate()
                process.join(0.5)
                if process.is_alive():
                    process.kill()
                    process.join()
                raise TimeoutError(
                    f"Wall-clock timeout exceeded {timeout_seconds:.2f} seconds."
                )
            if not response_queue.empty():
                status, *payload = response_queue.get()
                if status == "ok":
                    response, metadata = payload
                    active_client.set_last_response_metadata(metadata)
                    return response
                error_name, error_message = payload
                raise RuntimeError(f"{error_name}: {error_message}")
            raise RuntimeError("LLM worker exited without returning a response.")
        if not hasattr(signal, "setitimer"):
            return self.send_message(
                message_content,
                llm_client=active_client,
                **request_kwargs,
            )

        def _timeout_handler(signum, frame):
            raise TimeoutError(
                f"Wall-clock timeout exceeded {timeout_seconds:.2f} seconds."
            )

        previous_handler = signal.getsignal(signal.SIGALRM)
        previous_timer = signal.getitimer(signal.ITIMER_REAL)
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
        try:
            return self.send_message(
                message_content,
                llm_client=active_client,
                **request_kwargs,
            )
        finally:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)
            signal.signal(signal.SIGALRM, previous_handler)

    def reset_turn_decision_log(self) -> None:
        self.turn_decision_log = []
        self.turn_time_exhausted = False

    def configure_llm_interaction_logger(
        self, logger: Optional[Callable[[Dict[str, object]], None]]
    ) -> None:
        self.llm_interaction_logger = logger

    def configure_provider_pause_handler(
        self,
        handler: Optional[Callable[[Dict[str, object]], None]],
    ) -> None:
        self.provider_pause_handler = handler

    def set_interaction_context(
        self,
        *,
        game_round: int,
        turn_number: Optional[int],
        scope: str,
    ) -> None:
        self.current_game_round = game_round
        self.current_turn_number = turn_number
        self.current_interaction_scope = scope

    def _record_llm_decision(
        self,
        *,
        phase: str,
        prompt: str,
        llm_client: LLMClient,
        client_role: str,
        response: str,
        used_fallback_response: bool,
        error: Optional[str],
        timeout_seconds: Optional[float],
        decision_time_seconds: float,
        reasoning_effort_override: Optional[str],
        response_metadata: Optional[Dict[str, object]] = None,
        requested_timeout_seconds: Optional[float] = None,
        remaining_turn_time_seconds: Optional[float] = None,
        usable_turn_time_seconds: Optional[float] = None,
    ) -> str:
        error_type = None
        if error:
            error_type = error.split(":", 1)[0]
        usage = None
        if response_metadata is not None:
            usage = response_metadata.get("usage")

        decision_entry = {
            "interaction_index": None,
            "phase": phase,
            "scope": self.current_interaction_scope,
            "provider": getattr(llm_client, "provider_name", "unknown"),
            "model": getattr(llm_client, "model_type", "unknown"),
            "client_role": client_role,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "raw_response": response,
            "used_fallback_response": used_fallback_response,
            "error": error,
            "error_type": error_type,
            "timeout_seconds": timeout_seconds,
            "requested_timeout_seconds": requested_timeout_seconds,
            "remaining_turn_time_seconds": remaining_turn_time_seconds,
            "usable_turn_time_seconds": usable_turn_time_seconds,
            "decision_time_seconds": decision_time_seconds,
            "reasoning_effort_override": reasoning_effort_override,
            "usage": usage,
        }
        self.turn_decision_log.append(decision_entry)

        if self.llm_interaction_logger is not None:
            self._interaction_sequence += 1
            decision_entry["interaction_index"] = self._interaction_sequence
            interaction_entry = {
                "logged_at_utc": (
                    datetime.now(timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                "interaction_index": self._interaction_sequence,
                "player": self.name,
                "provider": getattr(llm_client, "provider_name", "unknown"),
                "model": getattr(llm_client, "model_type", "unknown"),
                "client_role": client_role,
                "scope": self.current_interaction_scope,
                "game_round": self.current_game_round,
                "turn_number": self.current_turn_number,
                "phase": phase,
                "request": {
                    "prompt": prompt,
                    "prompt_length": len(prompt),
                    "reasoning_effort_override": reasoning_effort_override,
                    "timeout_seconds": timeout_seconds,
                    "requested_timeout_seconds": requested_timeout_seconds,
                    "remaining_turn_time_seconds": remaining_turn_time_seconds,
                    "usable_turn_time_seconds": usable_turn_time_seconds,
                },
                "response": {
                    "raw_response": response,
                    "response_length": len(response),
                    "used_fallback_response": used_fallback_response,
                    "decision_time_seconds": decision_time_seconds,
                    "error": error,
                    "error_type": error_type,
                    "usage": usage,
                    "metadata": response_metadata,
                },
            }
            try:
                self.llm_interaction_logger(interaction_entry)
            except Exception as exc:
                print(f"Warning: failed to write LLM interaction log: {exc}")

        return response

    def _record_provider_pause_interaction(
        self,
        *,
        phase: str,
        prompt: str,
        llm_client: LLMClient,
        client_role: str,
        error: str,
        timeout_seconds: Optional[float],
        requested_timeout_seconds: Optional[float],
        remaining_turn_time_seconds: Optional[float],
        usable_turn_time_seconds: Optional[float],
        reasoning_effort_override: Optional[str],
    ) -> None:
        if self.llm_interaction_logger is None:
            return

        self._interaction_sequence += 1
        interaction_entry = {
            "logged_at_utc": (
                datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            ),
            "interaction_index": self._interaction_sequence,
            "entry_type": "provider_pause_error",
            "player": self.name,
            "provider": getattr(llm_client, "provider_name", "unknown"),
            "model": getattr(llm_client, "model_type", "unknown"),
            "client_role": client_role,
            "scope": self.current_interaction_scope,
            "game_round": self.current_game_round,
            "turn_number": self.current_turn_number,
            "phase": phase,
            "request": {
                "prompt": prompt,
                "prompt_length": len(prompt),
                "reasoning_effort_override": reasoning_effort_override,
                "timeout_seconds": timeout_seconds,
                "requested_timeout_seconds": requested_timeout_seconds,
                "remaining_turn_time_seconds": remaining_turn_time_seconds,
                "usable_turn_time_seconds": usable_turn_time_seconds,
            },
            "response": {
                "raw_response": "",
                "response_length": 0,
                "used_fallback_response": False,
                "error": error,
                "error_type": error.split(":", 1)[0] if error else None,
                "decision_time_seconds": 0.0,
                "usage": None,
                "metadata": None,
            },
        }
        self.llm_interaction_logger(interaction_entry)

    def _format_seconds_with_milliseconds(
        self, seconds: Optional[float]
    ) -> str:
        if seconds is None:
            return "unbounded"
        return f"{seconds:.3f} seconds"

    def _compute_prompt_budget(
        self,
        phase: str,
        requested_timeout_seconds: Optional[float],
    ) -> Dict[str, Optional[float]]:
        remaining_turn_time = self.remaining_turn_time_seconds()
        usable_turn_time = None
        effective_timeout = requested_timeout_seconds
        timeout_derived_from_turn_budget = False

        if remaining_turn_time is not None:
            if remaining_turn_time <= 0:
                usable_turn_time = 0.0
                effective_timeout = 0.0
            else:
                if phase == "initial_troop_placement":
                    usable_turn_time = remaining_turn_time
                else:
                    usable_turn_time = max(
                        remaining_turn_time - self.TURN_TIMEOUT_SAFETY_MARGIN_SECONDS,
                        0.0,
                    )
                if effective_timeout is None:
                    timeout_derived_from_turn_budget = True
                    effective_timeout = usable_turn_time
                else:
                    effective_timeout = min(effective_timeout, usable_turn_time)

        return {
            "remaining_turn_time_seconds": remaining_turn_time,
            "usable_turn_time_seconds": usable_turn_time,
            "effective_timeout_seconds": effective_timeout,
            "timeout_derived_from_turn_budget": timeout_derived_from_turn_budget,
        }

    def _format_time_budget_block(
        self,
        phase: str,
        requested_timeout_seconds: Optional[float],
    ) -> str:
        if not self.prompt_include_time_budget:
            return ""

        budget = self._compute_prompt_budget(phase, requested_timeout_seconds)
        remaining_turn_time = budget["remaining_turn_time_seconds"]
        usable_turn_time = budget["usable_turn_time_seconds"]
        effective_timeout = budget["effective_timeout_seconds"]

        lines = ["TIME BUDGET:"]
        if remaining_turn_time is not None:
            lines.append(
                "- Remaining total turn time right now: "
                f"{self._format_seconds_with_milliseconds(remaining_turn_time)}."
            )
            if phase != "initial_troop_placement" and usable_turn_time is not None:
                lines.append(
                    "- Usable turn time after the safety buffer: "
                    f"{self._format_seconds_with_milliseconds(usable_turn_time)}."
                )
        if effective_timeout is not None:
            lines.append(
                "- Hard timeout for this decision: "
                f"{self._format_seconds_with_milliseconds(effective_timeout)}."
            )
        lines.append(
            "- Act decisively. Prefer a legal move now over overanalyzing."
        )
        if phase == "attack":
            lines.append(
                "- If a favorable attack chain opens up, keep the sequence moving quickly one legal attack at a time."
            )
        return "\n".join(lines) + "\n"

    def _format_final_check(self, reminders: List[str]) -> str:
        if not self.prompt_repeat_key_points:
            return ""
        formatted = "\n".join(f"- {reminder}" for reminder in reminders)
        return f"FINAL CHECK:\n{formatted}\n"

    def _canonicalize_territory_name(self, text: str) -> Optional[str]:
        cleaned = (
            text.replace("**", " ")
            .replace("`", " ")
            .replace("_", " ")
            .strip(" -:;,.()[]{}")
        )
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
        return _TERRITORY_NAME_LOOKUP.get(cleaned)

    def _extract_attack_chain_steps(self) -> List[Tuple[str, str]]:
        plan_text = (self.turn_strategy or "").replace("→", "->")
        if "->" not in plan_text:
            return []

        steps: List[Tuple[str, str]] = []
        seen: set[Tuple[str, str]] = set()

        for raw_line in plan_text.splitlines():
            if "->" not in raw_line:
                continue
            resolved_tokens: List[str] = []
            for segment in re.split(r"\s*->\s*", raw_line):
                match = _TERRITORY_NAME_PATTERN.search(segment)
                if not match:
                    continue
                canonical = self._canonicalize_territory_name(match.group(0))
                if canonical:
                    resolved_tokens.append(canonical)
            for from_territory, to_territory in zip(
                resolved_tokens, resolved_tokens[1:]
            ):
                pair = (from_territory, to_territory)
                if pair not in seen:
                    steps.append(pair)
                    seen.add(pair)
        return steps

    def _build_attack_plan_guidance(
        self,
        game_state: "GameState",
        possible_attack_vectors: Dict[str, List],
        successful_attacks: int,
    ) -> str:
        if not self.prompt_use_attack_plan_handoff:
            return ""
        chain_steps = self._extract_attack_chain_steps()
        if not chain_steps:
            return ""

        chain_text = " -> ".join(
            [chain_steps[0][0]] + [target for _, target in chain_steps]
        )
        completed_steps = 0
        planned_next: Optional[Tuple[int, str, str, int]] = None

        for index, (from_territory, to_territory) in enumerate(chain_steps, start=1):
            legal_targets = possible_attack_vectors.get(from_territory)
            currently_controls_target = game_state.check_terr_control(
                self.name, to_territory
            )
            if currently_controls_target and (
                not legal_targets or to_territory not in legal_targets[1]
            ):
                completed_steps += 1
                continue
            if legal_targets and to_territory in legal_targets[1]:
                planned_next = (
                    index,
                    from_territory,
                    to_territory,
                    int(legal_targets[0]),
                )
                break

        lines = ["PLAN EXECUTION:"]
        lines.append(f"- Saved attack chain from your turn plan: {chain_text}.")
        if completed_steps:
            lines.append(
                f"- You already completed {completed_steps} planned step(s) from that chain."
            )
        if planned_next is not None:
            step_number, from_territory, to_territory, max_troops = planned_next
            lines.append(
                "- Planned next legal attack right now: "
                f"step {step_number}, {from_territory} -> {to_territory} "
                f"(max={max_troops})."
            )
            if successful_attacks > 0:
                lines.append(
                    "- Continue the chain now unless that step became illegal or the position changed materially."
                )
                lines.append(
                    "- Do not re-plan the whole board from scratch after every successful capture."
                )
            else:
                lines.append(
                    "- If this line is still favorable, start with that planned step."
                )
        else:
            lines.append(
                "- No remaining planned chain step is currently legal. Re-evaluate from the legal attack list."
            )
        return "\n".join(lines) + "\n"

    def get_turn_decision_log(self) -> List[Dict[str, object]]:
        return [dict(entry) for entry in self.turn_decision_log]

    def get_latest_turn_decision(self) -> Optional[Dict[str, object]]:
        if not self.turn_decision_log:
            return None
        return dict(self.turn_decision_log[-1])

    def start_turn_timer(self, time_limit_seconds: Optional[int] = None) -> None:
        limit = (
            self.turn_time_limit_seconds
            if time_limit_seconds is None
            else time_limit_seconds
        )
        self.turn_deadline = time.time() + limit
        self.turn_time_exhausted = False

    def clear_turn_timer(self) -> None:
        self.turn_deadline = None

    def remaining_turn_time_seconds(self) -> Optional[float]:
        if self.turn_deadline is None:
            return None
        return max(self.turn_deadline - time.time(), 0.0)

    def _default_fallback_response(self, phase: str) -> str:
        fallback_responses = {
            "initial_troop_placement": (
                "Move:|||Blank, 0|||\n"
                "Reasoning:+++LLM call failed; engine fallback requested.+++"
            ),
            "troop_placement": (
                "Move 1: |||Blank, 0|||\n"
                "Reasoning:+++LLM call failed; engine fallback requested.+++"
            ),
            "fortify": (
                "To Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++LLM call failed; skipping fortify.+++"
            ),
            "attack": (
                "Attack Opponent Territory:|||Blank, 0|||\n"
                "From Territory:###Blank###\n"
                "Reasoning:+++LLM call failed; stopping attacks.+++"
            ),
            "optional_card_trade": "||| 0 |||",
            "pre_turn_planning": "- Hold borders.\n- Avoid risky attacks.",
        }
        return fallback_responses.get(phase, "")

    def _client_for_phase(self, phase: str) -> Tuple[LLMClient, str]:
        if phase == "pre_turn_planning" and self.planning_llm_client is not None:
            return self.planning_llm_client, "planning"
        return self.llm_client, "primary"

    def _resolve_reasoning_effort_for_call(
        self,
        reasoning_effort: Optional[str],
        llm_client: Optional[LLMClient] = None,
    ) -> Optional[str]:
        active_client = self.llm_client if llm_client is None else llm_client
        if reasoning_effort is None:
            return None

        if getattr(active_client, "provider_name", "") != "OpenAI":
            return reasoning_effort

        if not getattr(active_client, "supports_reasoning", False):
            return None

        supported_efforts_resolver = getattr(
            active_client, "supported_reasoning_efforts", None
        )
        if not callable(supported_efforts_resolver):
            return reasoning_effort

        try:
            supported_efforts = tuple(
                supported_efforts_resolver(getattr(active_client, "model_type", ""))
            )
        except Exception:
            return reasoning_effort

        if not supported_efforts:
            return None
        if reasoning_effort in supported_efforts:
            return reasoning_effort
        if reasoning_effort not in self.REASONING_EFFORT_ORDER:
            return supported_efforts[0]

        requested_index = self.REASONING_EFFORT_ORDER.index(reasoning_effort)
        ranked_efforts = []
        for effort in supported_efforts:
            if effort not in self.REASONING_EFFORT_ORDER:
                ranked_efforts.append((999, 999, effort))
                continue
            supported_index = self.REASONING_EFFORT_ORDER.index(effort)
            ranked_efforts.append(
                (abs(supported_index - requested_index), supported_index, effort)
            )

        ranked_efforts.sort()
        return ranked_efforts[0][2]

    def _send_prompt_with_logging(
        self,
        phase: str,
        prompt: str,
        fallback_response: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        used_fallback_response = False
        error = None
        effective_timeout = timeout_seconds
        started_at = time.time()
        active_client, client_role = self._client_for_phase(phase)
        resolved_reasoning_effort = self._resolve_reasoning_effort_for_call(
            reasoning_effort,
            llm_client=active_client,
        )
        budget = self._compute_prompt_budget(phase, timeout_seconds)
        remaining_turn_time = budget["remaining_turn_time_seconds"]
        usable_turn_time = budget["usable_turn_time_seconds"]
        effective_timeout = budget["effective_timeout_seconds"]
        timeout_derived_from_turn_budget = bool(
            budget["timeout_derived_from_turn_budget"]
        )

        if remaining_turn_time is not None:
            if remaining_turn_time <= 0:
                used_fallback_response = True
                error = "Turn timer expired before prompt call."
                self.turn_time_exhausted = True
                response = (
                    fallback_response
                    if fallback_response is not None
                    else self._default_fallback_response(phase)
                )
                return self._record_llm_decision(
                    phase=phase,
                    prompt=prompt,
                    llm_client=active_client,
                    client_role=client_role,
                    response=response,
                    used_fallback_response=used_fallback_response,
                    error=error,
                    timeout_seconds=0,
                    requested_timeout_seconds=timeout_seconds,
                    remaining_turn_time_seconds=remaining_turn_time,
                    usable_turn_time_seconds=usable_turn_time,
                    decision_time_seconds=0.0,
                    reasoning_effort_override=resolved_reasoning_effort,
                )

            if effective_timeout <= 0:
                used_fallback_response = True
                error = "Turn timer usable budget exhausted before prompt call."
                self.turn_time_exhausted = True
                response = (
                    fallback_response
                    if fallback_response is not None
                    else self._default_fallback_response(phase)
                )
                return self._record_llm_decision(
                    phase=phase,
                    prompt=prompt,
                    llm_client=active_client,
                    client_role=client_role,
                    response=response,
                    used_fallback_response=used_fallback_response,
                    error=error,
                    timeout_seconds=0,
                    requested_timeout_seconds=timeout_seconds,
                    remaining_turn_time_seconds=remaining_turn_time,
                    usable_turn_time_seconds=usable_turn_time,
                    decision_time_seconds=0.0,
                    reasoning_effort_override=resolved_reasoning_effort,
                )

        while True:
            try:
                if os.getenv("RISK_DEBUG_TIMING") == "1":
                    print(
                        f"[TIMING] {self.name} phase={phase} "
                        f"timeout={effective_timeout} requested_reasoning={reasoning_effort} "
                        f"resolved_reasoning={resolved_reasoning_effort}"
                    )
                response = self._call_llm_with_timeout(
                    prompt,
                    llm_client=active_client,
                    timeout_seconds=effective_timeout,
                    reasoning_effort=resolved_reasoning_effort,
                    max_attempts_override=1 if effective_timeout is not None else None,
                )
                response_metadata = active_client.get_last_response_metadata()
                break
            except Exception as exc:
                error = str(exc)[:1200]
                response_metadata = None
                pause_signal = detect_provider_pause_signal(error)
                if pause_signal is not None and self.provider_pause_handler is not None:
                    self._record_provider_pause_interaction(
                        phase=phase,
                        prompt=prompt,
                        llm_client=active_client,
                        client_role=client_role,
                        error=error,
                        timeout_seconds=effective_timeout,
                        requested_timeout_seconds=timeout_seconds,
                        remaining_turn_time_seconds=remaining_turn_time,
                        usable_turn_time_seconds=usable_turn_time,
                        reasoning_effort_override=resolved_reasoning_effort,
                    )
                    self.provider_pause_handler(
                        {
                            "signal": pause_signal,
                            "provider": getattr(active_client, "provider_name", "unknown"),
                            "model": getattr(active_client, "model_type", "unknown"),
                            "player_name": self.name,
                            "phase": phase,
                            "client_role": client_role,
                            "scope": self.current_interaction_scope,
                            "error": error,
                        }
                    )
                    error = None
                    started_at = time.time()
                    continue
                used_fallback_response = True
                if isinstance(exc, TimeoutError) and timeout_derived_from_turn_budget:
                    self.turn_time_exhausted = True
                if (
                    self.turn_deadline is not None
                    and self.remaining_turn_time_seconds() is not None
                    and self.remaining_turn_time_seconds() <= 0
                ):
                    self.turn_time_exhausted = True
                if fallback_response is None:
                    fallback_response = self._default_fallback_response(phase)
                response = fallback_response
                break
        if used_fallback_response:
            response_metadata = None
        decision_time_seconds = round(time.time() - started_at, 3)
        if os.getenv("RISK_DEBUG_TIMING") == "1":
            print(
                f"[TIMING] {self.name} phase={phase} completed "
                f"in {decision_time_seconds}s fallback={used_fallback_response}"
            )
        return self._record_llm_decision(
            phase=phase,
            prompt=prompt,
            llm_client=active_client,
            client_role=client_role,
            response=response,
            used_fallback_response=used_fallback_response,
            error=error,
            timeout_seconds=effective_timeout,
            requested_timeout_seconds=timeout_seconds,
            remaining_turn_time_seconds=remaining_turn_time,
            usable_turn_time_seconds=usable_turn_time,
            decision_time_seconds=decision_time_seconds,
            reasoning_effort_override=resolved_reasoning_effort,
            response_metadata=response_metadata,
        )

    def _format_error_feedback(self, error_msg: Optional[str]) -> str:
        if not error_msg:
            return ""
        return (
            "LAST INVALID MOVE:\n"
            f"{error_msg}\n"
            "Do not repeat that mistake.\n\n"
        )
    
    def parse_response_strategy(self, move_response: object) -> str:
        response = move_response.strip()
        response = response[:1200]
        return response

    def parse_response_text(
        self,
        move_response: object,
        *,
        single_move_only: bool = False,
    ) -> Tuple[List[Dict[str, int]], Optional[str], Optional[str]]:
        response = move_response.strip()
        # print(f"Response content: {response}")

        # Regular expression to extract all moves (e.g., |||Territory, 3|||)
        move_matches = re.findall(r'\|\|\|\s*(.+?)\s*,\s*(\d+)\s*\|\|\|', response)
        reasoning_match = re.search(r'\+\+\+\s*(.+?)\s*\+\+\+', response)
        from_territory_match = re.search(r'\#\#\#\s*(.+?)\s*\#\#\#', response)

        moves = []
        reasoning = None
        from_territory = None

        # print(f"move_matches: {move_matches}")  # Debugging print
        # print(f"reasoning_match: {reasoning_match}")  # Debugging print
        # print(f"from_territory_match: {from_territory_match}")  # Debugging print

        if move_matches:
            if single_move_only:
                move_matches = [move_matches[-1]]
            for match in move_matches:
                territory_name = match[0].strip()
                num_troops = int(match[1].strip())
                moves.append({
                    'territory_name': territory_name,
                    'num_troops': num_troops
                })

            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                reasoning = reasoning[:1200]

            if from_territory_match:
                from_territory = from_territory_match.group(1).strip()

            return moves, reasoning, from_territory
        else:
            response = response[:1200]
            print(f"------__------Error parsing response: ------__------" +
                  f"{response}")
            return [{'territory_name': None, 'num_troops': None}], None, None
        
    def parse_card_trade_response(
        self, move_response: object
    ) -> Tuple[Optional[List[int]], Optional[str]]:
        """
        Parses the player's response regarding card trade suggestions during the Risk card trade phase.
        
        Parameters:
        - move_response: The response object returned by the player agent (e.g., LLM).
        
        Returns:
        - A tuple where:
        - The first element is a list of card numbers to trade, or None if no trade is suggested.
        - The second element is an optional string containing reasoning, if provided.
        """
        response = move_response.strip()

        # Regular expression to extract card trade suggestions (e.g., ||| 1, 3, 4 |||)
        trade_match = re.search(r'\|\|\|\s*(0|(?:\d+(?:\s*,\s*\d+)*))\s*\|\|\|', response)
        
        # Optional reasoning extraction (if any)
        reasoning_match = re.search(r'\+\+\+\s*(.+?)\s*\+\+\+', response)
        
        trade_cards = None
        reasoning = None

        # Check if a trade suggestion was found
        if trade_match:
            card_numbers = trade_match.group(1)
            trade_cards = [int(num.strip()) for num in card_numbers.split(',')]
        
            # Extract reasoning, if provided
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                reasoning = reasoning[:1200]

            return trade_cards, reasoning
        else:
            response = response[:1200]
            print(f"------__------Error parsing response: ------__------" +
                  f"{response}")
            return trade_cards, reasoning
        
    def format_list_of_cards(self, cards: List['Card']) -> str:
        # Step 1: Convert the list of cards into a formatted string
        list_of_cards = ""
        for index, card in enumerate(cards, start=1):
            list_of_cards += f"{index}. {card.territory} {card.troop_type}\n"
        return list_of_cards
  
    def format_valid_combinations(self, 
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]) -> str:
        formatted_combinations = ""
        
        for value, combinations in valid_combinations.items():
            for combination, wildcard_used in combinations:
                wildcard_text = "Wildcard used" if wildcard_used else "Wildcard not used"
                formatted_combinations += f"{value} troops: {combination} ({wildcard_text})\n"
        
        return formatted_combinations

    def _mandatory_trade_fallback_response(
        self, valid_combinations: Dict[int, List[Tuple[List[int], bool]]]
    ) -> str:
        for troop_value in sorted(valid_combinations.keys(), reverse=True):
            combinations = valid_combinations[troop_value]
            if not combinations:
                continue
            combination, _ = combinations[0]
            selected_cards = ", ".join(str(card_number) for card_number in combination)
            return (
                f"List of cards to trade ||| {selected_cards} |||\n"
                "Reasoning:+++LLM call failed; trading the best available set.+++"
            )
        return "||| 0 |||"
        
        
    def make_initial_troop_placement(
            self, rules: 'Rules', 
            game_state: 'GameState', error_msg: Optional[str] = None
    ) -> str:
        placement_state = game_state.format_placement_state_for_player(self.name)
        placement_targets = game_state.format_placement_targets_with_context(self.name)
        time_budget_block = self._format_time_budget_block(
            "initial_troop_placement",
            self.placement_time_limit_seconds,
        )
        prompt = f"""
PHASE:
Initial troop placement

PLAYER:
You are {self.name}

DECISION:
Choose exactly 1 territory you control and place exactly 1 troop on it.

PACE:
This is a fast local decision.
Pick quickly from the legal targets and avoid deep analysis.

{time_budget_block}

LEGAL CONSTRAINTS:
- You must choose one territory from your legal placement targets.
- You must place exactly 1 troop.
- Return only the action block in the required format.

{self._format_error_feedback(error_msg)}RULES:
        {rules}

CURRENT STATE:
        {placement_state}

LEGAL PLACEMENT TARGETS:
{placement_targets}

OUTPUT FORMAT:
        Move:|||Territory, Number of troops|||
        Reasoning:+++Reasoning for move+++

EXAMPLE:
        Move:|||Brazil, 1|||
        Reasoning:+++Brazil is a key territory in South America.+++

RESPONSE RULES:
- Keep reasoning brief.
- One sentence of reasoning maximum.
- Do not restate the game state.
- Do not explain the rules.
{self._format_final_check([
    "Choose exactly 1 legal territory you control.",
    "Place exactly 1 troop.",
    "Return only the action block.",
    f"Finish within the hard timeout shown above.",
])}
        """
        parsed_response = (
            self.parse_response_text(
                self._send_prompt_with_logging(
                    "initial_troop_placement",
                    prompt,
                    reasoning_effort=self.placement_reasoning_effort,
                    timeout_seconds=self.placement_time_limit_seconds,
                ),
                single_move_only=True,
            )
        )
        return parsed_response

    def make_troop_placement(
            self, rules: 'Rules',
            game_state: 'GameState',  error_msg: Optional[str] = None
    ) -> str:
        placement_state = game_state.format_placement_state_for_player(self.name)
        placement_targets = game_state.format_placement_targets_with_context(self.name)
        time_budget_block = self._format_time_budget_block(
            "troop_placement",
            self.placement_time_limit_seconds,
        )

        prompt = f"""
PHASE:
Troop placement

PLAYER:
You are {self.name}

DECISION:
Distribute all {self.troops} available troops across territories you control.

PACE:
This is still a fast placement phase.
Prefer a strong practical allocation over exhaustive analysis.

{time_budget_block}

LEGAL CONSTRAINTS:
- You may place troops only on territories you control.
- The total troops placed across all moves must equal {self.troops}.
- Return only the action block in the required format.

{self._format_error_feedback(error_msg)}RULES:
        {rules}

CURRENT STATE:
        {placement_state}

LEGAL PLACEMENT TARGETS:
{placement_targets}

OUTPUT FORMAT:

        Move 1: |||Territory, Number of troops|||

        Move 2: |||Territory, Number of troops|||

        Move 3: |||Territory, Number of troops|||

        For as many moves as you need to place all your troops.

        Reasoning:+++Reasoning for move+++

EXAMPLE:

        Move 1: |||Brazil, 1|||

        Move 2: |||Argentina, 2|||

        Move 3: |||Peru, 4|||

        Reasoning: +++Brazil, Argentina and Peru are key in South America+++

RESPONSE RULES:
- Keep reasoning brief.
- One sentence of reasoning maximum.
- Do not restate the game state.
- Do not explain the rules.
{self._format_final_check([
    f"Place all {self.troops} troops exactly once across legal territories you control.",
    "Use only legal placement targets.",
    "Return only the action block.",
    "Do not spend the whole clock on this placement step.",
])}
        """
        parsed_response = (
            self.parse_response_text(
                self._send_prompt_with_logging(
                    "troop_placement",
                    prompt,
                    reasoning_effort=self.placement_reasoning_effort,
                    timeout_seconds=self.placement_time_limit_seconds,
                ))
        )

        return parsed_response
    
    def make_fortify_move(
            self, rules: 'Rules',
            game_state: 'GameState', error_msg: Optional[str] = None
    ) -> str:
        current_game_state = game_state.format_game_state_for_player(
            self.name, include_world_map=False
        )
        formatted_fortify_options = game_state.format_fortify_options(self.name)
        time_budget_block = self._format_time_budget_block("fortify", None)


        prompt = f"""
PHASE:
Fortify

PLAYER:
You are {self.name}

DECISION:
Choose one legal fortify move or skip fortifying.

{time_budget_block}

LEGAL CONSTRAINTS:
- You may move troops only between connected territories you control.
- You must leave at least 1 troop behind in the source territory.
- Use one of the legal fortify options listed below, or skip.
- Return only the action block in the required format.

{self._format_error_feedback(error_msg)}RULES:
        {rules}

CURRENT STATE:
        {current_game_state}

LEGAL OPTIONS:
        {formatted_fortify_options}

TURN PLAN:
{self.turn_strategy}

OUTPUT FORMAT:
        To Territory:|||To Territory, Number of troops|||
        From Territory: ### From Territory ###
        Reasoning:+++Reasoning for move+++

EXAMPLE:
        To Territory:|||Brazil, 10|||
        From Territory:###Argentina###

        Reasoning:+++I need more troops in Brazil+++

SKIP FORMAT:
        To Territory:|||Blank, 0|||
        From Territory:###Blank###
        Reasoning:+++I don't want to fortify+++

RESPONSE RULES:
- Keep reasoning brief.
- Do not restate the game state.
- Do not explain the rules.
{self._format_final_check([
    "Choose one listed legal fortify move or skip.",
    "Leave at least 1 troop behind in the source territory.",
    "Return only the action block.",
    "If no fortify clearly helps, skip quickly.",
])}
        """
        parsed_response = (
            self.parse_response_text(
                self._send_prompt_with_logging(
                    "fortify",
                    prompt,
                    reasoning_effort=self.fortify_reasoning_effort,
                ),
                single_move_only=True,
            )
        )

        return parsed_response

    def make_attack_move(
            self, rules: 'Rules', 
            game_state: 'GameState', successful_attacks: int, 
            error_msg: Optional[str] = None
    ) -> str:
        current_game_state = game_state.format_game_state_for_player(
            self.name, include_world_map=False
        )
        strong_territories = (
            game_state.get_strong_territories_with_troops(self.name))
        
        possible_attack_vectors = (
            game_state.get_adjacent_enemy_territories(
                self.name, strong_territories))
        
        formatted_attack_vectors = (
            game_state.format_adjacent_enemy_territories(
                possible_attack_vectors, player_name=self.name
            ))
        time_budget_block = self._format_time_budget_block("attack", None)
        attack_plan_guidance = self._build_attack_plan_guidance(
            game_state,
            possible_attack_vectors,
            successful_attacks,
        )

        prompt = f"""
PHASE:
Attack

PLAYER:
You are {self.name}

DECISION:
Choose one legal attack or end the attack phase.

PACE:
This phase is time-sensitive.
If you find a favorable breakthrough line, keep attacking quickly while each next move remains legal and favorable.

{time_budget_block}

LEGAL CONSTRAINTS:
- Choose one option from the legal attack list below, or skip.
- If you attack, `From Territory` must match the chosen legal attack source.
- You may attack with any positive troop count up to the listed maximum.
- If you are done attacking, return the skip format.
- Return only the action block in the required format.

TURN STATUS:
- Successful attacks so far this turn: {successful_attacks}
- If you win at least one attack during this turn, you earn a card at the end of the attack phase.

{self._format_error_feedback(error_msg)}RULES:
        {rules}

CURRENT STATE:
        {current_game_state}

LEGAL OPTIONS:
        {formatted_attack_vectors} 

TURN PLAN:
{self.turn_strategy}

{attack_plan_guidance}

OUTPUT FORMAT:

        Attack Opponent Territory:||| Territory, Number of troops|||
        From Territory: ### From Territory ###
        Reasoning:+++Reasoning for move+++

EXAMPLE:
        Attack Opponent Territory:|||Brazil, 3|||
        From Territory:###Argentina###

        Reasoning:+++I want to attack Brazil with 3 troops from Argentina
        because it will help give me control over South America+++

SKIP FORMAT:

        Attack Opponent Territory:|||Blank, 0|||
        From Territory:###Blank###
        Reasoning:+++I am finished attacking because I don't want to overextend+++

RESPONSE RULES:
- Keep reasoning brief.
- Do not restate the game state.
- Do not explain the rules.
{self._format_final_check([
    "Choose one listed legal attack or skip.",
    "Use a legal From Territory from the listed options.",
    "If a fast favorable chain is available, keep the sequence moving.",
    "If your saved plan has a next legal attack, continue it unless the board changed materially.",
    "Return only the action block before the time budget expires.",
])}
        """
        # print(f"---------------This is the attack prompt:----------------")
        # print(prompt)
        parsed_response = (
            self.parse_response_text(
                self._send_prompt_with_logging(
                    "attack",
                    prompt,
                    reasoning_effort=self.attack_reasoning_effort,
                ),
                single_move_only=True,
            )
        )

        return parsed_response

    
    def must_trade_cards(self, cards: List['Card'], game_state: 'GameState',
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]
        ) -> Tuple[Optional[List[int]], Optional[str]]:

        formatted_valid_combinations = self.format_valid_combinations(
            valid_combinations)

        list_of_cards = self.format_list_of_cards(cards)        
        time_budget_block = self._format_time_budget_block(
            "mandatory_card_trade",
            None,
        )
        
        prompt = f"""
PHASE:
Mandatory card trade

PLAYER:
You are {self.name}

DECISION:
You must choose exactly one valid card combination to trade now.

{time_budget_block}

LEGAL CONSTRAINTS:
- You must choose one combination from the valid combinations list below.
- Return only the card numbers in the required format.

CURRENT STATE:
{game_state.format_game_state_for_player(self.name, include_world_map=False)}

YOUR CARDS:

        {list_of_cards}

VALID COMBINATIONS:
Each line starts with the troop value you would receive.

        {formatted_valid_combinations}

OUTPUT FORMAT:

        List of cards to trade ||| [Card Numbers] |||

EXAMPLE:
        List of cards to trade ||| 1, 3, 4 |||

RESPONSE RULES:
- Choose one listed set only.
- Do not explain the rules.
- Keep any reasoning extremely short if included.
{self._format_final_check([
    "Choose exactly one valid listed set.",
    "Return only the card numbers in the required format.",
    "Do not delay this turn on card-trade analysis.",
])}
        """
        parsed_response = (
            self.parse_card_trade_response(
                self._send_prompt_with_logging(
                    "mandatory_card_trade",
                    prompt,
                    fallback_response=self._mandatory_trade_fallback_response(
                        valid_combinations
                    ),
                    reasoning_effort=self.card_trade_reasoning_effort,
                ))
        )

        return parsed_response
    

    def may_trade_cards(self, cards: List['Card'], game_state: 'GameState',
        valid_combinations: Dict[int, List[Tuple[List[int], bool]]]
        ) -> Tuple[Optional[List[int]], Optional[str]]:
        
        current_game_state = game_state.format_game_state_for_player(
            self.name, include_world_map=False
        )
        formatted_valid_combinations = self.format_valid_combinations(
            valid_combinations)

        list_of_cards = self.format_list_of_cards(cards)       
        time_budget_block = self._format_time_budget_block(
            "optional_card_trade",
            None,
        )
        
        prompt = f"""
PHASE:
Optional card trade

PLAYER:
You are {self.name}

DECISION:
Choose one valid card combination to trade now, or hold your cards.

{time_budget_block}

LEGAL CONSTRAINTS:
- If you trade, choose one combination from the valid combinations list below.
- If you do not want to trade, return `||| 0 |||`.
- Return only the action block in the required format.

CURRENT STATE:
{current_game_state}

YOUR CARDS:

        {list_of_cards}

VALID COMBINATIONS:
Each line starts with the troop value you would receive.

        {formatted_valid_combinations}

OUTPUT FORMAT:

        If you decide to trade in a set of cards, respond with the list of 
        card numbers in the format:

        List of cards to trade ||| Card Numbers (separated by commas) |||

        Example:
        List of cards to trade ||| 1, 3, 4 |||

        If you decide not to trade any cards, respond with:
        ||| 0 |||

        RESPONSE RULES:
        - Either choose one listed set or choose 0.
        - Do not explain the rules.
        - Keep any reasoning extremely short if included.
{self._format_final_check([
    "Either choose one valid listed set or choose 0.",
    "Return only the action block.",
    "Do not burn the turn clock on this choice unless it clearly matters.",
])}
        """
        parsed_response = (
            self.parse_card_trade_response(
                self._send_prompt_with_logging(
                    "optional_card_trade",
                    prompt,
                    reasoning_effort=self.card_trade_reasoning_effort,
                ))
        )

        return parsed_response
        
    
    def choose_capital(self, game_state: 'GameState') -> str:
        territories = game_state.get_player_territories(self.name)
        if not territories:
            raise ValueError(f"{self.name} has no territories to choose as a capital")

        capital = max(
            territories,
            key=lambda territory: (
                len(game_state.territories_graph.get(territory, [])),
                territory,
            ),
        )
        self.capital = capital
        return capital

    def define_strategy_for_move(self, rules: 'Rules',
            game_state: 'GameState') -> None:
        current_game_state = game_state.format_game_state_for_player(
            self.name, include_world_map=False
        )
        strong_territories = (
            game_state.get_strong_territories_with_troops(self.name))
        
        possible_attack_vectors = (
            game_state.get_adjacent_enemy_territories(
                self.name, strong_territories))
        
        formatted_attack_vectors = (
            game_state.format_adjacent_enemy_territories(
                possible_attack_vectors, player_name=self.name
            ))
        
        number_of_territories = len(game_state.get_player_territories(self.name))
        
        extra_territories_required_to_win = (
            game_state.territories_required_to_win - 
            number_of_territories)
        time_budget_block = self._format_time_budget_block(
            "pre_turn_planning",
            self.planning_time_limit_seconds,
        )


        prompt = f"""
PHASE:
Pre-turn planning

PLAYER:
You are {self.name}

DECISION:
Write a very short plan for this turn before choosing actions.

PACE:
The later action prompts share the same turn timer.
Name the clearest reinforcement point and the fastest promising attack chain, if one exists.

{time_budget_block}

RULES:
{rules}

CURRENT STATE:
{current_game_state}

LEGAL ATTACK OVERVIEW:
{formatted_attack_vectors}

CONTEXT:
- Territories you control: {number_of_territories}
- Extra territories needed to reach the win target: {extra_territories_required_to_win}

OUTPUT FORMAT:
- Two short bullet points maximum.
- Focus on where to reinforce, where to attack if at all, and where to fortify.
- If you see a promising multi-step breakthrough, write it explicitly as `Territory -> Territory -> Territory`.

RESPONSE RULES:
- Maximum 60 words total.
- Do not restate the full board.
- Be concrete and concise.
{self._format_final_check([
    "Use two short bullet points maximum.",
    "Name the main reinforcement point.",
    "Name the clearest fast attack line if there is one.",
    "If you name an attack chain, use explicit Territory -> Territory notation.",
    "Stay concise so you preserve time for execution.",
])}
        """
        parsed_response = (
            self.parse_response_strategy(
                self._send_prompt_with_logging(
                    "pre_turn_planning",
                    prompt,
                    reasoning_effort=self.planning_reasoning_effort,
                    timeout_seconds=self.planning_time_limit_seconds,
                ))
        )
        

        self.turn_strategy = parsed_response

    def _get_strategic_advice(self, game_state: 'GameState') -> str:
        """Get relevant strategic advice from the knowledge base"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            from sentence_transformers import SentenceTransformer
            
            # Connect to knowledge base
            client = QdrantClient(host="qdrant", port=6333, check_compatibility=False)
            embedder = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Determine current game phase and card situation
            num_territories = len(game_state.get_player_territories(self.name))
            phase = "early" if num_territories < 10 else ("mid" if num_territories < 20 else "late")
            
            # For now, assume mid card bucket - you can enhance this logic later
            card_bucket = "mid"
            
            # Query for relevant strategic advice
            query_vector = embedder.encode("attack strategy elimination timing").tolist()
            
            # Get strategies for current phase and card situation
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                results = client.search(
                    collection_name="risk_tactics_kb",
                    query_vector=query_vector,
                    query_filter=Filter(
                        must=[
                            FieldCondition(key="phase", match=MatchValue(value=phase)),
                            FieldCondition(key="card_bucket", match=MatchValue(value=card_bucket))
                        ]
                    ),
                    limit=2
                )
            
            if not results:
                return "Focus on strategic attacks that maximize territorial gain while minimizing losses."
            
            # Format the top 2 strategic snippets
            advice = "Based on expert Risk strategy:\n\n"
            for i, result in enumerate(results[:2], 1):
                snippet = result.payload['snippet']
                # Remove the snippet title for cleaner integration
                clean_snippet = snippet.split('\n', 1)[1] if '\n' in snippet else snippet
                advice += f"{i}. {clean_snippet}\n\n"
            
            return advice.strip()
            
        except Exception as e:
            # Fallback if knowledge base is unavailable
            print(f"Warning: Could not access strategic knowledge base: {e}")
            return "Focus on strategic attacks that maximize territorial gain while minimizing losses."
