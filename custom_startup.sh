#!/bin/bash

echo "Current User:"
whoami

#echo "Environment Variables:"
#env

# Install Python packages for each service
pip install -e /app

# Execute the command
exec "$@"
# tail -f /dev/null
