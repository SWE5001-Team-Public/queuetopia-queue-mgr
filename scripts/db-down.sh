#!/bin/bash
set -e

DB_CONTAINER="queue-mgr-db"
DB_IMAGE="queuetopia-queue-mgr-db"

# Default compose file
COMPOSE_FILE="scripts/docker-compose-db.yml"

echo "Stopping and removing the PostgreSQL container..."
docker-compose -f "$COMPOSE_FILE" down -v

# Remove the database container if it still exists
if docker ps -a --format '{{.Names}}' | grep -q "^$DB_CONTAINER$"; then
    docker stop "$DB_CONTAINER"
    docker rm "$DB_CONTAINER"
    echo "✅ Removed container: $DB_CONTAINER"
else
    echo "⚠️ Container $DB_CONTAINER not found."
fi

# Remove the PostgreSQL image if it exists
if docker images -q "$DB_IMAGE" > /dev/null; then
    docker rmi -f "$DB_IMAGE"
    echo "✅ Removed image: $DB_IMAGE"
else
    echo "⚠️ Image $DB_IMAGE not found."
fi

echo "Cleaning up unused Docker resources..."
docker image prune -af --filter "label=project=queuetopia-queue-mgr"
docker volume rm queuetopia_queue_mgr_postgres_data

echo "✅ PostgreSQL container and image removed!"
