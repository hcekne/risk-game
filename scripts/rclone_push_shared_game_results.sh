#!/usr/bin/env bash

set -euo pipefail

REMOTE_PATH="${1:-dropbox:risk-game-shared/game_results}"
CONTAINER_NAME="${CONTAINER_NAME:-risk-game-container}"

docker exec \
  -e REMOTE_PATH="${REMOTE_PATH}" \
  "${CONTAINER_NAME}" \
  bash -lc 'rclone sync /shared-game-results "$REMOTE_PATH" --progress'
