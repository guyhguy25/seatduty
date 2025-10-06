#!/bin/bash
# Main startup script for SeatDuty Backend

ENVIRONMENT=${1:-development}

case $ENVIRONMENT in
    "development"|"dev")
        echo "🚀 Starting in DEVELOPMENT mode..."
        chmod +x scripts/start-dev.sh
        ./scripts/start-dev.sh
        ;;
    "production"|"prod")
        echo "🚀 Starting in PRODUCTION mode..."
        chmod +x scripts/start-prod.sh
        ./scripts/start-prod.sh
        ;;
    "test")
        echo "🧪 Running tests..."
        chmod +x scripts/test.sh
        ./scripts/test.sh
        ;;
    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: ./start.sh [development|production|test]"
        echo ""
        echo "Examples:"
        echo "  ./start.sh development  # Start development environment"
        echo "  ./start.sh production   # Start production environment"
        echo "  ./start.sh test         # Run tests"
        echo "  ./start.sh              # Default to development"
        exit 1
        ;;
esac
