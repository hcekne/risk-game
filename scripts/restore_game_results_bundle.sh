#!/usr/bin/env bash

set -euo pipefail

REMOTE_BUNDLES_PATH="${1:-dropbox:risk-game-shared/bundles}"
BUNDLE_NAME="${2:-latest_game_results.tar.gz}"
FORCE_CLEAR="${3:-}"
CONTAINER_NAME="${CONTAINER_NAME:-risk-game-container}"
TMP_DIR="/tmp/risk-game-bundles"

docker exec \
  -e REMOTE_BUNDLES_PATH="${REMOTE_BUNDLES_PATH}" \
  -e BUNDLE_NAME="${BUNDLE_NAME}" \
  -e FORCE_CLEAR="${FORCE_CLEAR}" \
  -e TMP_DIR="${TMP_DIR}" \
  "${CONTAINER_NAME}" \
  bash -lc '
set -euo pipefail

mkdir -p "$TMP_DIR" /shared-game-results
TAR_PATH="$TMP_DIR/$BUNDLE_NAME"

if [[ "${FORCE_CLEAR}" == "--force" ]]; then
  find /shared-game-results -mindepth 1 -maxdepth 1 -exec rm -rf {} +
else
  if find /shared-game-results -mindepth 1 -print -quit | grep -q .; then
    echo "Shared game_results is not empty. Re-run with --force to replace it."
    exit 2
  fi
fi

rclone copyto "$REMOTE_BUNDLES_PATH/$BUNDLE_NAME" "$TAR_PATH" --progress
tar -xzf "$TAR_PATH" -C /shared-game-results

echo "Restore complete."
echo "Restored bundle: $BUNDLE_NAME"
echo "Target path: /shared-game-results"
'
