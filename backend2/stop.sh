#!/bin/bash
# Stop script for SeatDuty Backend

# Usage:
#   ./stop.sh [--volumes|-v] [environment]
#   --volumes or -v: Remove named volumes as well
#   environment: development (default), production, test

REMOVE_VOLUMES=0
ENVIRONMENT="development"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --volumes|-v)
            REMOVE_VOLUMES=1
            shift
            ;;
        development|dev|production|prod|test)
            ENVIRONMENT=$arg
            shift
            ;;
        *)
            ;;
    esac
done

case $ENVIRONMENT in
    "development"|"dev")
        COMPOSE_FILE="docker-compose.yaml"
        ;;
    "production"|"prod")
        COMPOSE_FILE="docker-compose.prod.yaml"
        ;;
    "test")
        COMPOSE_FILE="docker-compose.test.yaml"
        ;;
    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: ./stop.sh [--volumes|-v] [development|production|test]"
        exit 1
        ;;
esac

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Compose file '$COMPOSE_FILE' not found!"
    exit 1
fi

echo "🛑 Stopping SeatDuty Backend ($ENVIRONMENT)..."

if [ $REMOVE_VOLUMES -eq 1 ]; then
    echo "⚠️  Removing containers and volumes..."
    docker compose -f "$COMPOSE_FILE" down -v
else
    echo "Stopping containers (volumes preserved)..."
    docker compose -f "$COMPOSE_FILE" down
fi

echo "✅ Stopped $ENVIRONMENT environment."
