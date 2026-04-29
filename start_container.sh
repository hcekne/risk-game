#!/bin/bash

set -euo pipefail

# Retrieve the user ID, group ID, and username
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USER_NAME=$(whoami)

# Print the user ID, group ID, and username
echo "User ID: $USER_ID"
echo "Group ID: $GROUP_ID"
echo "Username: $USER_NAME"

# Export variables for use in docker-compose
export USER_ID
export GROUP_ID
export USER_NAME

# Run Docker Compose with the appropriate user and group ID
docker-compose up --build -d

echo "Containers started in detached mode."
echo "Enter the app container with: docker exec -it risk-game-container bash"
echo "Run tests with: docker-compose exec -T risk-game pytest tests/"
