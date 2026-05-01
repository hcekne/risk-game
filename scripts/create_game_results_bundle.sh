#!/usr/bin/env bash

set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-risk-game-container}"
BUNDLE_LABEL="${1:-}"
TMP_DIR="/tmp/risk-game-bundles"

docker exec \
  -e BUNDLE_LABEL="${BUNDLE_LABEL}" \
  -e TMP_DIR="${TMP_DIR}" \
  "${CONTAINER_NAME}" \
  bash -lc '
set -euo pipefail

mkdir -p "$TMP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
if [[ -n "${BUNDLE_LABEL}" ]]; then
  SAFE_LABEL=$(printf "%s" "$BUNDLE_LABEL" | tr -cs "A-Za-z0-9._-" "_")
  BUNDLE_BASE="risk-game_game-results_${STAMP}_${SAFE_LABEL}"
else
  BUNDLE_BASE="risk-game_game-results_${STAMP}"
fi

TAR_PATH="$TMP_DIR/${BUNDLE_BASE}.tar.gz"
MANIFEST_PATH="$TMP_DIR/${BUNDLE_BASE}.manifest.txt"

mkdir -p /shared-game-results
tar -czf "$TAR_PATH" -C /shared-game-results .

SHA256=$(sha256sum "$TAR_PATH" | awk "{print \$1}")
SIZE=$(du -h "$TAR_PATH" | awk "{print \$1}")
COMMIT=$(git -C /app rev-parse HEAD)
BRANCH=$(git -C /app rev-parse --abbrev-ref HEAD)

cat > "$MANIFEST_PATH" <<EOF
bundle=${BUNDLE_BASE}.tar.gz
sha256=${SHA256}
size=${SIZE}
branch=${BRANCH}
commit=${COMMIT}
created_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
extract_into=/shared-game-results
archive_contents=game_results_root_contents
EOF

printf "BUNDLE_BASE=%s\n" "$BUNDLE_BASE"
printf "BUNDLE_TAR=%s\n" "$TAR_PATH"
printf "BUNDLE_MANIFEST=%s\n" "$MANIFEST_PATH"
printf "BUNDLE_SHA256=%s\n" "$SHA256"
printf "BUNDLE_SIZE=%s\n" "$SIZE"
'
