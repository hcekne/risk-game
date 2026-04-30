#!/bin/bash

if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "Run this script as 'bash start_container.sh', not '. start_container.sh'."
  return 1
fi

set -euo pipefail

# Retrieve the user ID, group ID, and username
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USER_NAME=$(whoami)
GAME_RESULTS_HOST_PATH="${GAME_RESULTS_HOST_PATH:-$HOME/shared/risk-game/game_results}"

# Print the user ID, group ID, and username
echo "User ID: $USER_ID"
echo "Group ID: $GROUP_ID"
echo "Username: $USER_NAME"
echo "Shared game_results path: $GAME_RESULTS_HOST_PATH"

# Export variables for use in docker-compose
export USER_ID
export GROUP_ID
export USER_NAME
export GAME_RESULTS_HOST_PATH

mkdir -p "$GAME_RESULTS_HOST_PATH"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Neither 'docker compose' nor 'docker-compose' is installed."
  echo "Install Docker with the Compose plugin, or install docker-compose."
  exit 127
fi

# Run Docker Compose with the appropriate user and group ID
"${COMPOSE_CMD[@]}" up --build -d

echo "Containers started in detached mode."
echo "Enter the app container with: docker exec -it risk-game-container bash"
echo "Run tests with: ${COMPOSE_CMD[*]} exec -T risk-game pytest tests/"
