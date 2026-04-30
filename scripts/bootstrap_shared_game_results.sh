#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/game_results"
TARGET_DIR="${GAME_RESULTS_HOST_PATH:-$HOME/shared/risk-game/game_results}"

mkdir -p "${TARGET_DIR}"

if find "${TARGET_DIR}" -mindepth 1 -print -quit | grep -q .; then
  echo "Shared game_results path already has content: ${TARGET_DIR}"
  exit 0
fi

echo "Bootstrapping shared game_results from ${SOURCE_DIR} to ${TARGET_DIR}"
cp -a "${SOURCE_DIR}/." "${TARGET_DIR}/"
echo "Bootstrap complete."
