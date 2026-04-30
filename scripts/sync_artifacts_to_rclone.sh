#!/usr/bin/env bash

set -euo pipefail

REMOTE_PATH="${1:-dropbox:risk-game-shared/game_results}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${RISK_GAME_RESULTS_DIR:-${REPO_ROOT}/game_results}"

echo "Syncing local artifacts from ${RESULTS_DIR} to ${REMOTE_PATH}"

rclone copy "${RESULTS_DIR}/experiments" "${REMOTE_PATH}/experiments" --progress
rclone copy "${RESULTS_DIR}/model_probes" "${REMOTE_PATH}/model_probes" --progress
rclone copy "${RESULTS_DIR}/prompt_smoke_runs" "${REMOTE_PATH}/prompt_smoke_runs" --progress
rclone copy "${RESULTS_DIR}/league_logs" "${REMOTE_PATH}/league_logs" --progress
rclone copy "${RESULTS_DIR}/rubric_calibration" "${REMOTE_PATH}/rubric_calibration" --progress

echo "Artifact sync complete."
