#!/usr/bin/env bash

set -euo pipefail

DEFAULT_REMOTE="dropbox:risk-game-shared/game_results"
REMOTE_PATH="${DEFAULT_REMOTE}"
RESYNC_FLAG=""
CONTAINER_NAME="${CONTAINER_NAME:-risk-game-container}"

for arg in "$@"; do
  case "$arg" in
    --resync)
      RESYNC_FLAG="--resync"
      ;;
    *)
      REMOTE_PATH="$arg"
      ;;
  esac
done

if [[ "${RESYNC_FLAG}" == "--resync" ]]; then
  docker exec \
    -e REMOTE_PATH="${REMOTE_PATH}" \
    "${CONTAINER_NAME}" \
    bash -lc 'mkdir -p /shared-game-results && rclone bisync /shared-game-results "$REMOTE_PATH" --resync --progress'
  exit 0
fi

docker exec \
  -e REMOTE_PATH="${REMOTE_PATH}" \
  "${CONTAINER_NAME}" \
  bash -lc 'mkdir -p /shared-game-results && rclone bisync /shared-game-results "$REMOTE_PATH" --progress'
