#!/usr/bin/env bash

set -euo pipefail

REMOTE_PATH="${1:-dropbox:risk-game-shared/game_results}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${RISK_GAME_RESULTS_DIR:-${REPO_ROOT}/game_results}"

mkdir -p \
  "${RESULTS_DIR}/experiments" \
  "${RESULTS_DIR}/model_probes" \
  "${RESULTS_DIR}/prompt_smoke_runs" \
  "${RESULTS_DIR}/league_logs" \
  "${RESULTS_DIR}/rubric_calibration"

echo "Restoring shared artifacts from ${REMOTE_PATH} into ${RESULTS_DIR}"

rclone copy "${REMOTE_PATH}/experiments" "${RESULTS_DIR}/experiments" --progress
rclone copy "${REMOTE_PATH}/model_probes" "${RESULTS_DIR}/model_probes" --progress
rclone copy "${REMOTE_PATH}/prompt_smoke_runs" "${RESULTS_DIR}/prompt_smoke_runs" --progress
rclone copy "${REMOTE_PATH}/league_logs" "${RESULTS_DIR}/league_logs" --progress
rclone copy "${REMOTE_PATH}/rubric_calibration" "${RESULTS_DIR}/rubric_calibration" --progress

echo "Artifact restore complete."
