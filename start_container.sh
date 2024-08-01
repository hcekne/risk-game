#!/bin/bash

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
docker-compose up --build



# Run Docker Compose with the appropriate user and group ID
# USER_ID=$USER_ID GROUP_ID=$GROUP_ID docker-compose up --build
