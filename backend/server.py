from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('DB_NAME', 'seatduty'),
    'user': os.getenv('DB_USER', 'seatduty_user'),
    'password': os.getenv('DB_PASSWORD', 'seatduty_password'),
    'port': os.getenv('DB_PORT', '5432')
}

# API Configuration
SCORES_API_URL = "https://webws.365scores.com/web/games/fixtures/"
DEFAULT_PARAMS = {
    "appTypeId": 5,
    "langId": 2,
    "timezoneName": "Asia/Jerusalem",
    "userCountryId": 6,
    "competitors": 579,  # Hapoel Beer Sheva team ID
    "showOdds": "true",
    "includeTopBettingOpportunity": 1,
    "topBookmaker": 1
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

class GameData:
    """Data model for game information"""
    def __init__(self, game_data: Dict[str, Any]):
        self.id = game_data.get('id')
        self.sport_id = game_data.get('sportId')
        self.competition_id = game_data.get('competitionId')
        self.season_num = game_data.get('seasonNum')
        self.stage_num = game_data.get('stageNum')
        self.round_num = game_data.get('roundNum')
        self.round_name = game_data.get('roundName')
        self.competition_display_name = game_data.get('competitionDisplayName')
        self.start_time = game_data.get('startTime')
        self.status_group = game_data.get('statusGroup')
        self.status_text = game_data.get('statusText')
        self.short_status_text = game_data.get('shortStatusText')
        self.game_time = game_data.get('gameTime')
        self.game_time_display = game_data.get('gameTimeDisplay')
        self.has_tv_networks = game_data.get('hasTVNetworks')
        self.home_competitor = game_data.get('homeCompetitor')
        self.away_competitor = game_data.get('awayCompetitor')
        self.is_home_away_inverted = game_data.get('isHomeAwayInverted')
        self.has_stats = game_data.get('hasStats')
        self.has_standings = game_data.get('hasStandings')
        self.standings_name = game_data.get('standingsName')
        self.has_brackets = game_data.get('hasBrackets')
        self.has_previous_meetings = game_data.get('hasPreviousMeetings')
        self.has_recent_matches = game_data.get('hasRecentMatches')
        self.winner = game_data.get('winner')
        self.home_away_team_order = game_data.get('homeAwayTeamOrder')
        self.has_point_by_point = game_data.get('hasPointByPoint')
        self.has_video = game_data.get('hasVideo')
        self.odds = game_data.get('odds')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'sportId': self.sport_id,
            'competitionId': self.competition_id,
            'seasonNum': self.season_num,
            'stageNum': self.stage_num,
            'roundNum': self.round_num,
            'roundName': self.round_name,
            'competitionDisplayName': self.competition_display_name,
            'startTime': self.start_time,
            'statusGroup': self.status_group,
            'statusText': self.status_text,
            'shortStatusText': self.short_status_text,
            'gameTime': self.game_time,
            'gameTimeDisplay': self.game_time_display,
            'hasTVNetworks': self.has_tv_networks,
            'homeCompetitor': self.home_competitor,
            'awayCompetitor': self.away_competitor,
            'isHomeAwayInverted': self.is_home_away_inverted,
            'hasStats': self.has_stats,
            'hasStandings': self.has_standings,
            'standingsName': self.standings_name,
            'hasBrackets': self.has_brackets,
            'hasPreviousMeetings': self.has_previous_meetings,
            'hasRecentMatches': self.has_recent_matches,
            'winner': self.winner,
            'homeAwayTeamOrder': self.home_away_team_order,
            'hasPointByPoint': self.has_point_by_point,
            'hasVideo': self.has_video,
            'odds': self.odds
        }

def fetch_games_data() -> Optional[Dict[str, Any]]:
    """Fetch games data from 365scores API"""
    try:
        response = requests.get(SCORES_API_URL, params=DEFAULT_PARAMS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def get_home_games(api_data: Dict[str, Any], team_id: int = 579, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Filter and return home games for the specified team
    Equivalent to the JavaScript logic provided
    """
    if not api_data or 'games' not in api_data:
        return []
    
    # Use timezone-aware current time
    current_time = datetime.now(timezone.utc)
    home_games = []
    
    for game in api_data['games']:
        # Check if it's a home game for the specified team
        home_competitor = game.get('homeCompetitor')
        if not home_competitor or home_competitor.get('id') != team_id:
            continue
            
        # Check if the game is in the future
        try:
            # Parse the ISO format datetime with timezone
            game_start_time = datetime.fromisoformat(game['startTime'].replace('Z', '+00:00'))
            if game_start_time > current_time:
                home_games.append(game)
        except (ValueError, KeyError) as e:
            print(f"Error parsing game start time: {e}")
            continue
    
    # Sort by start time and limit results
    home_games.sort(key=lambda x: x['startTime'])
    return home_games[:limit]

def store_game_in_db(game_data: Dict[str, Any]) -> bool:
    """Store game data in database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Parse start time
            start_time = datetime.fromisoformat(game_data['startTime'].replace('Z', '+00:00'))
            
            # Prepare values
            values = (
                game_data['id'], 
                game_data.get('sportId'), 
                game_data.get('competitionId'),
                game_data.get('seasonNum'), 
                game_data.get('stageNum'), 
                game_data.get('roundNum'),
                game_data.get('roundName'), 
                game_data.get('competitionDisplayName'),
                start_time, 
                game_data.get('statusGroup'), 
                game_data.get('statusText'),
                game_data.get('shortStatusText'), 
                game_data.get('gameTime'),
                game_data.get('gameTimeDisplay'), 
                game_data.get('hasTVNetworks'),
                game_data.get('homeCompetitor', {}).get('id'),
                game_data.get('awayCompetitor', {}).get('id'),
                game_data.get('homeCompetitor', {}).get('name'),
                game_data.get('awayCompetitor', {}).get('name'),
                game_data.get('isHomeAwayInverted'), 
                game_data.get('hasStats'),
                game_data.get('hasStandings'), 
                game_data.get('standingsName'),
                game_data.get('hasBrackets'), 
                game_data.get('hasPreviousMeetings'),
                game_data.get('hasRecentMatches'), 
                game_data.get('winner'),
                game_data.get('homeAwayTeamOrder'), 
                game_data.get('hasPointByPoint'),
                game_data.get('hasVideo')
            )
            
            print(f"DEBUG: Number of values: {len(values)}")
            
            # Insert or update game
            cur.execute("""
                INSERT INTO games (
                    id, sport_id, competition_id, season_num, stage_num, round_num,
                    round_name, competition_display_name, start_time, status_group,
                    status_text, short_status_text, game_time, game_time_display,
                    has_tv_networks, home_competitor_id, away_competitor_id,
                    home_competitor_name, away_competitor_name, is_home_away_inverted,
                    has_stats, has_standings, standings_name, has_brackets,
                    has_previous_meetings, has_recent_matches, winner,
                    home_away_team_order, has_point_by_point, has_video
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    status_text = EXCLUDED.status_text,
                    short_status_text = EXCLUDED.short_status_text,
                    updated_at = CURRENT_TIMESTAMP
            """, values)
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error storing game in database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_available_users_for_game(game_start_time: datetime) -> List[Dict[str, Any]]:
    """Get users available for a specific game based on day of week"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            day_of_week = game_start_time.weekday()  # 0=Monday, 6=Sunday
            # Convert to our format: 0=Sunday, 1=Monday, ..., 6=Saturday
            day_of_week = (day_of_week + 1) % 7
            
            cur.execute("""
                SELECT u.id, u.name, u.email, us.total_games_assigned, us.last_assigned_at
                FROM users u
                JOIN user_availability ua ON u.id = ua.user_id
                LEFT JOIN user_stats us ON u.id = us.user_id
                WHERE u.is_active = true 
                AND ua.day_of_week = %s 
                AND ua.is_available = true
                ORDER BY us.total_games_assigned ASC, us.last_assigned_at ASC NULLS FIRST
            """, (day_of_week,))
            
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error getting available users: {e}")
        return []
    finally:
        conn.close()

def assign_users_to_game(game_id: int, user_ids: List[int]) -> bool:
    """Assign users to a game"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Insert assignments
            for user_id in user_ids:
                cur.execute("""
                    INSERT INTO seat_duty_assignments (user_id, game_id, status)
                    VALUES (%s, %s, 'assigned')
                    ON CONFLICT (user_id, game_id) DO NOTHING
                """, (user_id, game_id))
            
            # Update user stats
            for user_id in user_ids:
                cur.execute("""
                    INSERT INTO user_stats (user_id, total_games_assigned, last_assigned_game_id, last_assigned_at)
                    VALUES (%s, 1, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        total_games_assigned = user_stats.total_games_assigned + 1,
                        last_assigned_game_id = %s,
                        last_assigned_at = CURRENT_TIMESTAMP
                """, (user_id, game_id, game_id))
            
            # Mark game as assigned
            cur.execute("""
                UPDATE games SET is_assigned = true WHERE id = %s
            """, (game_id,))
            
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error assigning users to game: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_game_assignments(game_id: int) -> List[Dict[str, Any]]:
    """Get assigned users for a specific game"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT sda.user_id, u.name, sda.status
                FROM seat_duty_assignments sda
                JOIN users u ON sda.user_id = u.id
                WHERE sda.game_id = %s
                ORDER BY sda.assigned_at ASC
            """, (game_id,))
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error getting game assignments: {e}")
        return []
    finally:
        conn.close()

def is_game_fully_assigned(game_id: int) -> bool:
    """Check if a game already has 2 users assigned"""
    assignments = get_game_assignments(game_id)
    return len(assignments) >= 2

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Webhook endpoint for seat duty"""
    try:
        # Fetch data from 365scores API
        api_data = fetch_games_data()
        
        if not api_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch data from 365scores API'
            }), 500
        
        # Get home games for Hapoel Beer Sheva (team ID 579)
        home_games = get_home_games(api_data, team_id=579, limit=6)
        
        # Store games in database and handle assignments
        assignments_made = []
        enhanced_games = []
        
        for game in home_games:
            # Store game in database
            store_game_in_db(game)
            
            # Get current assignments for this game
            current_assignments = get_game_assignments(game['id'])
            
            # Check if game needs assignment (less than 2 users)
            if len(current_assignments) < 2:
                game_start_time = datetime.fromisoformat(game['startTime'].replace('Z', '+00:00'))
                available_users = get_available_users_for_game(game_start_time)
                
                # If we have enough available users, assign them
                if len(available_users) >= (2 - len(current_assignments)):
                    # Get the users with least assignments (fairness algorithm)
                    needed_users = 2 - len(current_assignments)
                    selected_users = available_users[:needed_users]
                    user_ids = [user['id'] for user in selected_users]
                    
                    # Assign users to game
                    if assign_users_to_game(game['id'], user_ids):
                        assignments_made.append({
                            'game_id': game['id'],
                            'game_time': game['startTime'],
                            'assigned_users': [{'id': u['id'], 'name': u['name']} for u in selected_users]
                        })
                        # Refresh assignments after new assignment
                        current_assignments = get_game_assignments(game['id'])
            
            # Add assigned users info to game data
            game_with_assignments = game.copy()
            game_with_assignments['assigned_user_names'] = [assignment['name'] for assignment in current_assignments]
            game_with_assignments['assignedUserId'] = [assignment['user_id'] for assignment in current_assignments]
            enhanced_games.append(game_with_assignments)
        
        return jsonify({
            'success': True,
            'data': enhanced_games,
            'total_games': len(enhanced_games),
            'team_id': 579,
            'assignments_made': assignments_made,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/games', methods=['GET'])
def get_games():
    """Direct endpoint to get games data"""
    try:
        # Get query parameters
        team_id = request.args.get('team_id', 579, type=int)
        limit = request.args.get('limit', 6, type=int)
        
        # Fetch data from API
        api_data = fetch_games_data()
        
        if not api_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch data from 365scores API'
            }), 500
        
        # Get home games
        home_games = get_home_games(api_data, team_id=team_id, limit=limit)
        
        return jsonify({
            'success': True,
            'games': home_games,
            'total_games': len(home_games),
            'team_id': team_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users with their stats"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT u.id, u.name, u.email, u.is_active,
                       us.total_games_assigned, us.total_games_completed,
                       us.last_assigned_at
                FROM users u
                LEFT JOIN user_stats us ON u.id = us.user_id
                ORDER BY u.name
            """)
            users = cur.fetchall()
            
            return jsonify({
                'success': True,
                'users': [dict(user) for user in users],
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    except psycopg2.Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/assignments', methods=['GET'])
def get_assignments():
    """Get all current assignments"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT sda.id, sda.user_id, u.name as user_name, sda.game_id,
                       g.start_time, g.home_competitor_name, g.away_competitor_name,
                       sda.status, sda.assigned_at
                FROM seat_duty_assignments sda
                JOIN users u ON sda.user_id = u.id
                JOIN games g ON sda.game_id = g.id
                WHERE g.start_time > CURRENT_TIMESTAMP
                ORDER BY g.start_time ASC
            """)
            assignments = cur.fetchall()
            
            return jsonify({
                'success': True,
                'assignments': [dict(assignment) for assignment in assignments],
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    except psycopg2.Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Seat Duty API Server',
        'endpoints': {
            'webhook': '/webhook (POST/GET) - Main webhook with auto-assignment',
            'games': '/games (GET) - ?team_id=579&limit=6',
            'users': '/users (GET) - Get all users with stats',
            'assignments': '/assignments (GET) - Get current assignments',
            'health': '/health (GET)'
        },
        'default_team_id': 579,
        'features': [
            'Automatic user assignment based on availability',
            'Fairness algorithm (least assigned users first)',
            'Day-of-week constraints per user',
            'Database persistence',
            'Real-time game data from 365scores'
        ],
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

if __name__ == '__main__':
    print("Starting Seat Duty API Server...")
    print("Available endpoints:")
    print("  - POST/GET /webhook - Main webhook endpoint")
    print("  - GET /games - Direct games endpoint")
    print("  - GET /health - Health check")
    print("  - GET / - API information")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
