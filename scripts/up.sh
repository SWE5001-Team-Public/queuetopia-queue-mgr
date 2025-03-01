#!/bin/bash
set -e

# Move to the project root (where Dockerfile is located)
cd "$(dirname "$0")/.." || exit

# Run down.sh first to stop and clean up existing containers
echo "Stopping existing containers before starting fresh..."
bash scripts/down.sh

# Check for --dev flag
if [[ "$1" == "--dev" ]]; then
    COMPOSE_FILE="scripts/docker-compose-dev.yml"
    echo "Using development docker-compose file: $COMPOSE_FILE"
else
	COMPOSE_FILE="scripts/docker-compose.yml"
    echo "Using production docker-compose file: $COMPOSE_FILE"
fi

echo "Building the Docker image..."
docker build -t queue-mgr .

echo "Starting the Docker container with $COMPOSE_FILE..."
docker-compose -f "$COMPOSE_FILE" -p queuetopia_queue_mgr up -d --build

echo "Checking running containers..."
docker ps
