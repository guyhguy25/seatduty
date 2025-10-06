#!/bin/bash
# Development startup script

echo "🚀 Starting SeatDuty Backend in DEVELOPMENT mode..."

# Load development environment variables
if [ -f "env.development" ]; then
    export $(cat env.development | grep -v '^#' | xargs)
    echo "✅ Loaded development environment variables"
else
    echo "⚠️  No env.development file found, using defaults"
fi

# Start development services
docker compose -f docker-compose.yaml up --build -d

echo "🎉 Development environment started!"
echo "📊 API: http://localhost:8001"
echo "🗄️  Database: localhost:5433"
echo "🧪 Test DB: localhost:5434"
