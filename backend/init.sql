-- Initialize database for seat duty application
-- This file will be executed when the PostgreSQL container starts for the first time

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_availability table for day constraints
CREATE TABLE IF NOT EXISTS user_availability (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL, -- 0=Sunday, 1=Monday, ..., 6=Saturday
    is_available BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, day_of_week)
);

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    sport_id INTEGER,
    competition_id INTEGER,
    season_num INTEGER,
    stage_num INTEGER,
    round_num INTEGER,
    round_name VARCHAR(255),
    competition_display_name VARCHAR(255),
    start_time TIMESTAMP,
    status_group INTEGER,
    status_text VARCHAR(255),
    short_status_text VARCHAR(255),
    game_time REAL,
    game_time_display VARCHAR(50),
    has_tv_networks BOOLEAN,
    home_competitor_id INTEGER,
    away_competitor_id INTEGER,
    home_competitor_name VARCHAR(255),
    away_competitor_name VARCHAR(255),
    is_home_away_inverted BOOLEAN,
    has_stats BOOLEAN,
    has_standings BOOLEAN,
    standings_name VARCHAR(255),
    has_brackets BOOLEAN,
    has_previous_meetings BOOLEAN,
    has_recent_matches BOOLEAN,
    winner INTEGER,
    home_away_team_order INTEGER,
    has_point_by_point BOOLEAN,
    has_video BOOLEAN,
    is_assigned BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create seat_duty_assignments table
CREATE TABLE IF NOT EXISTS seat_duty_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    seat_number VARCHAR(50),
    section VARCHAR(100),
    status VARCHAR(50) DEFAULT 'assigned', -- assigned, confirmed, completed, cancelled
    notes TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, game_id)
);

-- Create user_stats table to track fairness
CREATE TABLE IF NOT EXISTS user_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total_games_assigned INTEGER DEFAULT 0,
    total_games_completed INTEGER DEFAULT 0,
    last_assigned_game_id INTEGER REFERENCES games(id),
    last_assigned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games(start_time);
CREATE INDEX IF NOT EXISTS idx_games_home_competitor ON games(home_competitor_id);
CREATE INDEX IF NOT EXISTS idx_games_is_assigned ON games(is_assigned);
CREATE INDEX IF NOT EXISTS idx_seat_duty_user_id ON seat_duty_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_seat_duty_game_id ON seat_duty_assignments(game_id);
CREATE INDEX IF NOT EXISTS idx_seat_duty_status ON seat_duty_assignments(status);
CREATE INDEX IF NOT EXISTS idx_user_availability_user_id ON user_availability(user_id);
CREATE INDEX IF NOT EXISTS idx_user_availability_day ON user_availability(day_of_week);
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);

-- Insert the 6 users
INSERT INTO users (name, email, phone) VALUES 
    ('Guy', 'guyhguy@gmail.com', '+972-52-468-9126'),
    ('Noam', 'noam@gmail.com', '+972-52-555-0903'),
    ('Itay', 'itay@gmail.com', '+972-52-668-9163'),
    ('Jonas', 'jonas@gmail.com', '+972-54-626-3225'),
    ('Tamir', 'tamir@gmail.com', '+972-52-585-9629'),
    ('Ben', 'ben@gmail.com', '+972-50-818-5868')
ON CONFLICT (email) DO NOTHING;

-- Set up user availability constraints
-- Guy and Tamir: All days except Monday (1) and Wednesday (3)
INSERT INTO user_availability (user_id, day_of_week, is_available) 
SELECT u.id, d.day, 
    CASE 
        WHEN d.day IN (1, 3) THEN false  -- Monday and Wednesday not available
        ELSE true 
    END
FROM users u, (SELECT 0 as day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d
WHERE u.name IN ('Guy', 'Tamir')
ON CONFLICT (user_id, day_of_week) DO NOTHING;

-- Itay and Jonas: All days available
INSERT INTO user_availability (user_id, day_of_week, is_available) 
SELECT u.id, d.day, true
FROM users u, (SELECT 0 as day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d
WHERE u.name IN ('Itay', 'Jonas')
ON CONFLICT (user_id, day_of_week) DO NOTHING;

-- Noam: All days except Saturday (6)
INSERT INTO user_availability (user_id, day_of_week, is_available) 
SELECT u.id, d.day, 
    CASE 
        WHEN d.day = 6 THEN false  -- Saturday not available
        ELSE true 
    END
FROM users u, (SELECT 0 as day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d
WHERE u.name = 'Noam'
ON CONFLICT (user_id, day_of_week) DO NOTHING;

-- Ben: Only Saturday (6)
INSERT INTO user_availability (user_id, day_of_week, is_available) 
SELECT u.id, d.day, 
    CASE 
        WHEN d.day = 6 THEN true   -- Only Saturday available
        ELSE false 
    END
FROM users u, (SELECT 0 as day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d
WHERE u.name = 'Ben'
ON CONFLICT (user_id, day_of_week) DO NOTHING;

-- Initialize user stats with current assignments
-- Guy, Noam, Tamir, Ben have 1 game assigned
INSERT INTO user_stats (user_id, total_games_assigned) 
SELECT id, 1 FROM users WHERE name IN ('Guy', 'Noam', 'Tamir', 'Ben')
ON CONFLICT (user_id) DO NOTHING;

-- Itay and Jonas have 0 games assigned (they will be assigned to next game)
INSERT INTO user_stats (user_id, total_games_assigned) 
SELECT id, 0 FROM users WHERE name IN ('Itay', 'Jonas')
ON CONFLICT (user_id) DO NOTHING;

-- Update completed games for users
UPDATE user_stats 
SET total_games_completed = 1 
WHERE user_id IN (
    SELECT id FROM users WHERE name IN ('Ben', 'Guy', 'Noam', 'Tamir')
);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_seat_duty_assignments_updated_at BEFORE UPDATE ON seat_duty_assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
