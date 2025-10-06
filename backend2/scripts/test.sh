#!/bin/bash
# Test runner script

echo "🧪 Running SeatDuty Backend Tests..."

# Load development environment variables
if [ -f "env.development" ]; then
    export $(cat env.development | grep -v '^#' | xargs)
fi

# Run tests
echo "Running pytest tests..."
docker compose -f docker-compose.yaml run test

echo "✅ Tests completed!"
