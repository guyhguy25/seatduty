#!/bin/bash
# Production startup script

echo "🚀 Starting SeatDuty Backend in PRODUCTION mode..."

# Check if production environment variables exist
if [ ! -f "env.production" ]; then
    echo "❌ Production environment file (env.production) not found!"
    echo "Please create env.production with your production settings:"
    echo "  - POSTGRES_PASSWORD=your_secure_password"
    echo "  - JWT_SECRET_KEY=your_super_secure_jwt_secret_key"
    exit 1
fi

# Load production environment variables
export $(cat env.production | grep -v '^#' | xargs)
echo "✅ Loaded production environment variables"

# Start production services
docker compose -f docker-compose.prod.yml up --build -d

echo "🎉 Production environment started!"
echo "📊 API: http://localhost:8000"
echo "🗄️  Database: localhost:5432"
echo "🌐 Nginx: http://localhost:80"
