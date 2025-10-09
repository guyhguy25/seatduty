# Club Management System

## Overview
The club management system allows groups to be associated with football clubs. It integrates with the 365scores API to fetch countries, competitions, and teams data.

## API Endpoints

### Club Data Endpoints

#### 1. Get Countries
```
GET /clubs/countries?force_refresh=false
```
Returns a list of countries with football leagues.

**Query Parameters:**
- `force_refresh` (optional, default: false): Force refresh from 365scores API

**Response:**
```json
[
  {
    "id": 6,
    "name": "Israel",
    "has_league": true
  }
]
```

**Caching:** Results are cached for 24 hours in `cache/countries.json`

---

#### 2. Get Competitions
```
GET /clubs/competitions?country_id={countryId}&force_refresh=false
```
Returns competitions for a specific country.

**Query Parameters:**
- `country_id` (required): Country ID from the countries endpoint
- `force_refresh` (optional, default: false): Force refresh from API

**Response:**
```json
[
  {
    "id": 42,
    "name": "Premier League",
    "image_path": "/competition/42.png",
    "country_id": 6,
    "current_season_num": 2024,
    "current_stage_num": 1
  }
]
```

**Caching:** Results are cached for 24 hours in `cache/competitions_{country_id}.json`

---

#### 3. Get Teams
```
GET /clubs/teams?competition_id={competitionId}&season_num={seasonNum}&stage_num={stageNum}&force_refresh=false
```
Returns teams from competition standings.

**Query Parameters:**
- `competition_id` (required): Competition ID
- `season_num` (optional): Season number (uses current if not provided)
- `stage_num` (optional): Stage number (uses current if not provided)
- `force_refresh` (optional, default: false): Force refresh from API

**Response:**
```json
[
  {
    "id": 1234,
    "name": "Manchester United",
    "image_url": "https://...",
    "country_name": "England"
  }
]
```

**Caching:** Results are cached for 24 hours in `cache/teams_{competition_id}_{season_num}_{stage_num}.json`

---

#### 4. Create Club from Team
```
POST /clubs/create-from-team?team_id={teamId}&team_name={name}&...
```
Creates or updates a club in the database from team selection.

**Query Parameters:**
- `team_id` (required): Team ID from 365scores
- `team_name` (required): Team name
- `team_image_url` (optional): Team logo URL
- `country_name` (optional): Country name
- `country_id` (optional): Country ID
- `competition_id` (optional): Competition ID
- `competition_name` (optional): Competition name

**Response:**
```json
{
  "id": 1,
  "name": "Manchester United",
  "external_id": "1234",
  "logo": "https://...",
  "country": "England",
  "country_id": "6",
  "competition_id": "42",
  "competition_name": "Premier League"
}
```

---

#### 5. List All Clubs
```
GET /clubs
```
Returns all clubs stored in the database.

---

#### 6. Get Club by ID
```
GET /clubs/{club_id}
```
Returns a specific club by its internal database ID.

---

### Group Creation with Club

When creating a group, you can now associate it with a club:

```
POST /groups
```

**Request Body:**
```json
{
  "name": "Manchester United Fans",
  "description": "Group for Man United supporters",
  "club_id": 1
}
```

The `club_id` is optional. If provided, it must reference an existing club in the database.

---

## Frontend Integration Flow

### Step 1: Fetch Countries
```javascript
const response = await fetch('/clubs/countries');
const countries = await response.json();
// Display countries to user
```

### Step 2: Fetch Competitions
```javascript
// After user selects a country
const countryId = selectedCountry.id;
const response = await fetch(`/clubs/competitions?country_id=${countryId}`);
const competitions = await response.json();
// Display competitions to user
```

### Step 3: Fetch Teams
```javascript
// After user selects a competition
const competitionId = selectedCompetition.id;
const response = await fetch(`/clubs/teams?competition_id=${competitionId}`);
const teams = await response.json();
// Display teams to user
```

### Step 4: Create Club and Group
```javascript
// After user selects a team
const selectedTeam = teams[0];

// First, create/update the club
const clubParams = new URLSearchParams({
  team_id: selectedTeam.id,
  team_name: selectedTeam.name,
  team_image_url: selectedTeam.image_url,
  country_name: selectedTeam.country_name,
  country_id: selectedCountry.id,
  competition_id: selectedCompetition.id,
  competition_name: selectedCompetition.name
});

const clubResponse = await fetch(`/clubs/create-from-team?${clubParams}`, {
  method: 'POST'
});
const club = await clubResponse.json();

// Then create the group with the club
const groupResponse = await fetch('/groups', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'My Group Name',
    description: 'Group description',
    club_id: club.id
  })
});
const group = await groupResponse.json();
```

---

## Database Schema

### clubs Table
```sql
CREATE TABLE clubs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  external_id VARCHAR(255) NOT NULL UNIQUE,
  logo TEXT,
  country VARCHAR(255),
  country_id VARCHAR(255),
  competition_id VARCHAR(255),
  competition_name VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### groups Table (updated)
```sql
-- Added column:
club_id INTEGER REFERENCES clubs(id)
```

---

## Caching System

### Cache Location
All API responses are cached in the `cache/` directory at the root of the backend.

### Cache Files
- `cache/countries.json` - Countries list
- `cache/competitions_{country_id}.json` - Competitions per country
- `cache/teams_{competition_id}_{season_num}_{stage_num}.json` - Teams per competition

### Cache Duration
- Default: 24 hours
- Can be bypassed with `force_refresh=true` query parameter

### Cache Invalidation
1. **Manual**: Delete cache files or set `force_refresh=true`
2. **Automatic**: Cache expires after 24 hours
3. **Fallback**: If API fails, stale cache is returned with a warning

---

## Error Handling

### API Failures
If the 365scores API is unavailable:
1. The system first tries to return cached data (even if expired)
2. If no cache exists, returns HTTP 503 with error details

### Invalid Club ID
If a non-existent `club_id` is provided during group creation:
- Returns HTTP 404 with "Club not found" message

---

## Migration

To apply database changes:

```bash
# If using docker-compose
docker-compose exec db psql -U postgres -d seatduty -f /migrations/add_club_to_groups.sql

# Or manually run the SQL in migrations/add_club_to_groups.sql
```

---

## Notes

1. **Cache Directory**: The `cache/` directory is automatically created on first API call
2. **External IDs**: Club `external_id` is the team ID from 365scores API
3. **Group Limit**: Users can still only create 2 groups maximum
4. **Club Optional**: The `club_id` field is optional when creating groups

