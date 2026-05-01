#!/usr/bin/env bash

set -euo pipefail

REMOTE_BUNDLES_PATH="${1:-dropbox:risk-game-shared/bundles}"
BUNDLE_NAME="${2:-latest_game_results.tar.gz}"
CONTAINER_NAME="${CONTAINER_NAME:-risk-game-container}"
TMP_DIR="/tmp/risk-game-bundles"

docker exec \
  -e REMOTE_BUNDLES_PATH="${REMOTE_BUNDLES_PATH}" \
  -e BUNDLE_NAME="${BUNDLE_NAME}" \
  -e TMP_DIR="${TMP_DIR}" \
  "${CONTAINER_NAME}" \
  bash -lc '
set -euo pipefail

mkdir -p "$TMP_DIR"
MANIFEST_NAME="${BUNDLE_NAME%.tar.gz}.manifest.txt"
TAR_PATH="$TMP_DIR/$BUNDLE_NAME"
MANIFEST_PATH="$TMP_DIR/$MANIFEST_NAME"

rclone copyto "$REMOTE_BUNDLES_PATH/$BUNDLE_NAME" "$TAR_PATH" --progress
rclone copyto "$REMOTE_BUNDLES_PATH/$MANIFEST_NAME" "$MANIFEST_PATH" --progress || true

printf "DOWNLOADED_TAR=%s\n" "$TAR_PATH"
printf "DOWNLOADED_MANIFEST=%s\n" "$MANIFEST_PATH"
if [[ -f "$MANIFEST_PATH" ]]; then
  cat "$MANIFEST_PATH"
fi
'
