-- Migration: Add club association to groups
-- Date: 2025-10-09

-- Add new columns to clubs table
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS country_id VARCHAR(255);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS competition_id VARCHAR(255);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS competition_name VARCHAR(255);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS symbolic_name VARCHAR(255);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS name_for_url VARCHAR(255);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS popularity_rank INTEGER;
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS color VARCHAR(50);
ALTER TABLE clubs ADD COLUMN IF NOT EXISTS away_color VARCHAR(50);

-- Add club_id foreign key to groups table
ALTER TABLE groups ADD COLUMN IF NOT EXISTS club_id INTEGER REFERENCES clubs(id);
CREATE INDEX IF NOT EXISTS idx_groups_club_id ON groups(club_id);

