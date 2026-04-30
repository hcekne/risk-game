#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

mkdir -p "${REPO_ROOT}/data/rclone-config" "${REPO_ROOT}/data/rclone-cache"

exec docker run --rm -it \
  --network host \
  --user "$(id -u):$(id -g)" \
  -e HOME=/home/hcekne \
  -v "${REPO_ROOT}/data/rclone-config:/home/hcekne/.config/rclone" \
  -v "${REPO_ROOT}/data/rclone-cache:/home/hcekne/.cache/rclone" \
  risk-game:latest \
  bash -lc 'rclone config'
