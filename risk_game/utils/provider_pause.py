from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class ProviderPauseSignal:
    category: str
    matched_substring: str
    error_message: str


class ProviderPauseAborted(RuntimeError):
    """Raised when the operator chooses to abort a paused live run."""


_PROVIDER_PAUSE_MATCHERS: tuple[tuple[str, str], ...] = (
    ("billing_or_quota", "insufficient_quota"),
    ("billing_or_quota", "credit balance is too low"),
    ("billing_or_quota", "quota exceeded"),
    ("billing_or_quota", "resource_exhausted"),
    ("billing_or_quota", "billing"),
    ("rate_limit", "rate limit"),
    ("rate_limit", "rate_limit"),
    ("rate_limit", "error code: 429"),
    ("authentication", "invalid api key"),
    ("authentication", "api key not valid"),
    ("authentication", "authenticationerror"),
)


def detect_provider_pause_signal(
    error_message: Optional[str],
) -> Optional[ProviderPauseSignal]:
    if not error_message:
        return None
    normalized = error_message.lower()
    for category, needle in _PROVIDER_PAUSE_MATCHERS:
        if needle in normalized:
            return ProviderPauseSignal(
                category=category,
                matched_substring=needle,
                error_message=error_message[:1200],
            )
    return None


class ExperimentPauseController:
    def __init__(
        self,
        *,
        experiment_folder: Path,
        manifest: Dict[str, object],
        input_func: Callable[[str], str] = input,
    ) -> None:
        self.experiment_folder = experiment_folder
        self.manifest = manifest
        self.input_func = input_func
        self.pause_events_path = experiment_folder / "experiment_pause_events.json"

    def _load_events(self) -> List[Dict[str, object]]:
        if not self.pause_events_path.exists():
            return []
        payload = json.loads(self.pause_events_path.read_text())
        return list(payload.get("events", []))

    def _write_events(self, events: List[Dict[str, object]]) -> None:
        self.pause_events_path.parent.mkdir(parents=True, exist_ok=True)
        self.pause_events_path.write_text(json.dumps({"events": events}, indent=2))

    def pause_for_provider_issue(
        self,
        *,
        signal: ProviderPauseSignal,
        provider: str,
        model: str,
        player_name: str,
        phase: str,
        client_role: str,
        scope: str,
        completed_games: int,
        current_game_index: Optional[int],
        current_seat_order: Optional[List[str]],
        last_completed_game_folder: Optional[str],
        last_winner: Optional[str],
    ) -> None:
        from risk_game.utils.experiment_batch import (
            build_experiment_status,
            write_experiment_status,
        )

        error_message = signal.error_message[:1200]
        paused_status = build_experiment_status(
            manifest=self.manifest,
            state="paused",
            experiment_folder=self.experiment_folder,
            completed_games=completed_games,
            current_game_index=current_game_index,
            current_seat_order=current_seat_order,
            last_completed_game_folder=last_completed_game_folder,
            last_winner=last_winner,
            error=error_message,
        )
        write_experiment_status(self.experiment_folder, paused_status)

        events = self._load_events()
        event: Dict[str, object] = {
            "paused_at_utc": paused_status["updated_at_utc"],
            "resumed_at_utc": None,
            "category": signal.category,
            "matched_substring": signal.matched_substring,
            "provider": provider,
            "model": model,
            "player_name": player_name,
            "phase": phase,
            "client_role": client_role,
            "scope": scope,
            "completed_games": completed_games,
            "current_game_index": current_game_index,
            "current_seat_order": current_seat_order,
            "last_completed_game_folder": last_completed_game_folder,
            "last_winner": last_winner,
            "error": error_message,
        }
        events.append(event)
        self._write_events(events)

        print(
            "PAUSED: provider failure requires operator action.\n"
            f"  provider={provider} model={model} player={player_name}\n"
            f"  phase={phase} client_role={client_role} scope={scope}\n"
            f"  category={signal.category} matched={signal.matched_substring}\n"
            f"  error={error_message}"
        )

        while True:
            try:
                response = self.input_func(
                    "Fix the provider issue, then press Enter to retry. "
                    "Type 'abort' to stop this run: "
                )
            except EOFError as exc:
                raise ProviderPauseAborted(
                    "Provider pause requested operator input, but stdin closed."
                ) from exc
            normalized = response.strip().lower()
            if normalized in ("", "retry", "resume", "continue"):
                break
            if normalized in ("abort", "fail", "quit", "q"):
                raise ProviderPauseAborted(
                    f"Operator aborted after provider pause: {provider}:{model} {phase}"
                )
            print("Unrecognized input. Press Enter to retry or type 'abort'.")

        resumed_status = build_experiment_status(
            manifest=self.manifest,
            state="running",
            experiment_folder=self.experiment_folder,
            completed_games=completed_games,
            current_game_index=current_game_index,
            current_seat_order=current_seat_order,
            last_completed_game_folder=last_completed_game_folder,
            last_winner=last_winner,
        )
        event["resumed_at_utc"] = resumed_status["updated_at_utc"]
        self._write_events(events)
        write_experiment_status(self.experiment_folder, resumed_status)
