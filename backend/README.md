# Seat Duty API Server

A Python Flask server that provides webhook functionality for seat duty management, fetching game data from the 365scores API.

## Features

- **Webhook Endpoint**: `/webhook` - Main endpoint for external integrations
- **Games API**: `/games` - Direct access to game data
- **Health Check**: `/health` - Server health monitoring
- **Home Games Filtering**: Automatically filters for Hapoel Beer Sheva home games (Team ID: 579)
- **Future Games Only**: Returns only upcoming games, sorted by start time

## Installation

### Option 1: Docker (Recommended)

1. **Build and run with Docker Compose:**
```bash
# Run only the API server
docker-compose up --build

# Run with database (for future use)
docker-compose --profile database up --build

# Run with database and Redis cache
docker-compose --profile database --profile cache up --build
```

2. **Or build and run manually:**
```bash
# Build the Docker image
docker build -t seat-duty-api .

# Run the container
docker run -p 5000:5000 seat-duty-api
```

### Option 2: Local Development

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST/GET `/webhook`
Main webhook endpoint that returns home games for Hapoel Beer Sheva.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "json": {
        "id": 4463521,
        "startTime": "2026-02-14T16:00:00+02:00",
        "homeCompetitor": {
          "id": 579,
          "name": "הפועל באר שבע"
        },
        "awayCompetitor": {
          "id": 567,
          "name": "הפועל תל אביב"
        },
        "competitionDisplayName": "ליגת העל"
      }
    }
  ],
  "total_games": 6,
  "team_id": 579,
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/games`
Direct endpoint to get games data with optional parameters.

**Parameters:**
- `team_id` (optional): Team ID to filter for (default: 579)
- `limit` (optional): Maximum number of games to return (default: 6)

**Example:**
```
GET /games?team_id=579&limit=10
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/`
API information and available endpoints.

## Configuration

The server is configured to fetch data from the 365scores API with the following default parameters:
- Team ID: 579 (Hapoel Beer Sheva)
- Language: Hebrew (langId: 2)
- Timezone: Asia/Jerusalem
- Country: Israel (userCountryId: 6)

## Data Structure

The server returns game data matching the TypeScript interfaces defined in `type.ts`, including:
- Game details (ID, start time, competition)
- Home and away competitors
- Game status and timing
- Odds information (when available)

## Usage Examples

### Webhook Call
```bash
curl -X POST http://localhost:5000/webhook
```

### Get Games
```bash
curl "http://localhost:5000/games?team_id=579&limit=3"
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Docker Services

The docker-compose.yml includes several services:

### Core Services
- **seat-duty-api**: Main Flask application server
- **postgres**: PostgreSQL database (profile: database)
- **redis**: Redis cache (profile: cache)

### Database Schema
The PostgreSQL database includes:
- `users` table for user management
- `games` table for storing game data
- `seat_duty_assignments` table for user-game assignments
- Automatic timestamp triggers
- Proper indexes for performance

### Docker Commands

```bash
# Start only the API server
docker-compose up

# Start with database
docker-compose --profile database up

# Start with database and Redis
docker-compose --profile database --profile cache up

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f seat-duty-api

# Rebuild and restart
docker-compose up --build --force-recreate
```

## Environment Variables

You can customize the application using environment variables:

```bash
# In docker-compose.yml or .env file
FLASK_ENV=production
POSTGRES_DB=seatduty
POSTGRES_USER=seatduty_user
POSTGRES_PASSWORD=seatduty_password
```

## Future Enhancements

- ✅ PostgreSQL database integration for user management
- ✅ Docker containerization
- User-to-game assignment functionality
- Authentication and authorization
- Rate limiting and caching
- Logging and monitoring
- API rate limiting
- Database connection pooling
