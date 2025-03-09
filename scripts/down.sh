#!/bin/bash
set -e

# Define container and image names
DB_CONTAINER="queue-mgr-db"
APP_IMAGE="queuetopia_queue_mgr-queue-mgr"
DB_IMAGE="queuetopia_queue_mgr-queue-mgr-postgres"

echo "Stopping and removing the Docker containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose -p queuetopia_queue_mgr down -v
else
    docker compose -p queuetopia_queue_mgr down -v
fi

# Stop and remove database container if running
FOUND_CONTAINER=$(docker ps -a --format '{{.Names}}' | grep "^$DB_CONTAINER$" || true)

if [[ -n "$FOUND_CONTAINER" ]]; then
    echo "Stopping and removing database container: $DB_CONTAINER..."
    docker stop "$DB_CONTAINER"
    docker rm "$DB_CONTAINER"
    echo "✅ Removed container: $DB_CONTAINER"
else
    echo "⚠️ Database container $DB_CONTAINER not found."
fi

echo "Removing Docker images..."
docker rmi -f "$APP_IMAGE" || echo "Image $APP_IMAGE not found."
docker rmi -f "$DB_IMAGE" || echo "Image $DB_IMAGE not found."

echo "Cleaning up unused Docker resources..."
docker image prune -af --filter "label=project=queuetopia-queue-mgr" || echo "No unused images to remove."

# Ensure Buildx images are also cleaned up (for multi-arch support)
docker buildx prune -af || echo "No Buildx cache to clear."

echo "Checking remaining running containers..."
docker ps -a
