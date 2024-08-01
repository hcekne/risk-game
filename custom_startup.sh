#!/bin/bash

echo "Current User:"
whoami

#echo "Environment Variables:"
#env

# Install Python packages for each service
pip install -e /app

tail -f /dev/null
