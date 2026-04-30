from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GAME_RESULTS_DIR = REPO_ROOT / "game_results"


def get_game_results_dir() -> Path:
    configured = os.environ.get("RISK_GAME_RESULTS_DIR")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_GAME_RESULTS_DIR


def get_game_results_subdir(*parts: str) -> Path:
    return get_game_results_dir().joinpath(*parts)
