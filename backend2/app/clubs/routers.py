from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.users.models import User
from app.groups.models import Club
from app.groups.schemas import ClubOut, CountryOut, CompetitionOut, TeamOut

router = APIRouter(prefix="/clubs", tags=["clubs"])

# Cache directory
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

COUNTRIES_CACHE_FILE = CACHE_DIR / "countries.json"
COMPETITIONS_CACHE_FILE = CACHE_DIR / "competitions.json"
TEAMS_CACHE_FILE = CACHE_DIR / "teams.json"

# Cache expiration time (in hours)
CACHE_EXPIRATION_HOURS = 24


def is_cache_valid(cache_file: Path) -> bool:
    """Check if cache file exists and is not expired."""
    if not cache_file.exists():
        return False
    
    # Check file modification time
    mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
    expiration_time = datetime.now() - timedelta(hours=CACHE_EXPIRATION_HOURS)
    return mtime > expiration_time


def read_cache(cache_file: Path):
    """Read data from cache file."""
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def write_cache(cache_file: Path, data):
    """Write data to cache file."""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


@router.get("/countries", response_model=list[CountryOut])
def get_countries(
    force_refresh: bool = Query(False, description="Force refresh from API"),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of countries with football leagues.
    Cached for 24 hours unless force_refresh is True.
    """
    # Check cache first
    if not force_refresh and is_cache_valid(COUNTRIES_CACHE_FILE):
        cached_data = read_cache(COUNTRIES_CACHE_FILE)
        if cached_data:
            return cached_data
    
    # Fetch from API
    try:
        url = "https://webws.365scores.com/web/countries/?appTypeId=5&langId=2&timezoneName=Asia/Jerusalem&userCountryId=6&sports=1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Transform data to our schema
        countries = []
        for country in data.get("countries", []):
            countries.append({
                "id": country.get("id"),
                "name": country.get("name"),
                "has_league": country.get("hasLeague", False)
            })
        
        # Cache the results
        write_cache(COUNTRIES_CACHE_FILE, countries)
        
        return countries
    except requests.RequestException as e:
        # If API fails, try to return cached data even if expired
        cached_data = read_cache(COUNTRIES_CACHE_FILE)
        if cached_data:
            return cached_data
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch countries: {str(e)}"
        )


@router.get("/competitions", response_model=list[CompetitionOut])
def get_competitions(
    country_id: int = Query(..., description="Country ID to filter competitions"),
    force_refresh: bool = Query(False, description="Force refresh from API"),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of competitions for a specific country.
    Cached for 24 hours unless force_refresh is True.
    """
    cache_key = f"competitions_{country_id}"
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    # Check cache first
    if not force_refresh and is_cache_valid(cache_file):
        cached_data = read_cache(cache_file)
        if cached_data:
            return cached_data
    
    # Fetch from API
    try:
        url = f"https://webws.365scores.com/web/competitions/?appTypeId=5&langId=2&timezoneName=Asia/Jerusalem&userCountryId=6&sports=1&countries={country_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Transform data to our schema
        competitions = []
        for comp in data.get("competitions", []):
            competitions.append({
                "id": comp.get("id"),
                "name": comp.get("name"),
                "image_path": comp.get("imagePath"),
                "country_id": comp.get("countryId"),
                "current_season_num": comp.get("currentSeasonNum"),
                "current_stage_num": comp.get("currentStageNum")
            })
        
        # Cache the results
        write_cache(cache_file, competitions)
        
        return competitions
    except requests.RequestException as e:
        # If API fails, try to return cached data even if expired
        cached_data = read_cache(cache_file)
        if cached_data:
            return cached_data
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch competitions: {str(e)}"
        )


@router.get("/teams", response_model=list[TeamOut])
def get_teams(
    competition_id: int = Query(..., description="Competition ID"),
    season_num: Optional[int] = Query(None, description="Season number (optional, uses current if not provided)"),
    stage_num: Optional[int] = Query(None, description="Stage number (optional, uses current if not provided)"),
    force_refresh: bool = Query(False, description="Force refresh from API"),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of teams from competition standings.
    Cached for 24 hours unless force_refresh is True.
    """
    # First, get competition details if season/stage not provided
    if season_num is None or stage_num is None:
        # Fetch competition to get current season/stage
        try:
            comp_url = f"https://webws.365scores.com/web/competitions/?appTypeId=5&langId=2&timezoneName=Asia/Jerusalem&userCountryId=6&sports=1"
            comp_response = requests.get(comp_url, timeout=10)
            comp_response.raise_for_status()
            comp_data = comp_response.json()
            
            # Find our competition
            for comp in comp_data.get("competitions", []):
                if comp.get("id") == competition_id:
                    if season_num is None:
                        season_num = comp.get("currentSeasonNum")
                    if stage_num is None:
                        stage_num = comp.get("currentStageNum")
                    break
        except Exception:
            # Use defaults if fetching fails
            season_num = season_num or 1
            stage_num = stage_num or 1
    
    cache_key = f"teams_{competition_id}_{season_num}_{stage_num}"
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    # Check cache first
    if not force_refresh and is_cache_valid(cache_file):
        cached_data = read_cache(cache_file)
        if cached_data:
            return cached_data
    
    # Fetch from API
    try:
        url = f"https://webws.365scores.com/web/standings/?appTypeId=5&langId=2&timezoneName=Asia/Jerusalem&userCountryId=6&competitions={competition_id}&live=false&isPreview=true&stageNum={stage_num}&seasonNum={season_num}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Transform data to our schema
        teams = []
        seen_teams = set()
        
        # Extract countries mapping from response
        countries_dict = {}
        for country in data.get("countries", []):
            countries_dict[country.get("id")] = country.get("name")
        
        for standing in data.get("standings", []):
            for row in standing.get("rows", []):
                competitor = row.get("competitor", {})
                team_id = competitor.get("id")
                
                # Skip duplicates
                if team_id in seen_teams:
                    continue
                seen_teams.add(team_id)
                
                # Get country info - try both countryId and country field
                country_id = competitor.get("countryId")
                if not country_id and competitor.get("country"):
                    # Handle if country is nested object
                    country_obj = competitor.get("country")
                    if isinstance(country_obj, dict):
                        country_id = country_obj.get("id")
                
                country_name = countries_dict.get(country_id) if country_id else None
                
                # Generate logo URL using 365scores image cache
                logo_url = f"https://imagecache.365scores.com/image/upload/f_png,w_68,h_68,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/{team_id}"
                
                teams.append({
                    "id": team_id,
                    "name": competitor.get("name"),
                    "image_url": logo_url,
                    "country_name": country_name,
                    "country_id": country_id,
                    "symbolic_name": competitor.get("symbolicName"),
                    "name_for_url": competitor.get("nameForURL"),
                    "popularity_rank": competitor.get("popularityRank"),
                    "color": competitor.get("color"),
                    "away_color": competitor.get("awayColor")
                })
        
        # Cache the results
        write_cache(cache_file, teams)
        
        return teams
    except requests.RequestException as e:
        # If API fails, try to return cached data even if expired
        cached_data = read_cache(cache_file)
        if cached_data:
            return cached_data
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch teams: {str(e)}"
        )


@router.post("/create-from-team", response_model=ClubOut)
def create_club_from_team(
    team_id: int = Query(..., description="Team ID from 365scores"),
    team_name: str = Query(..., description="Team name"),
    team_image_url: Optional[str] = Query(None, description="Team image URL"),
    country_name: Optional[str] = Query(None, description="Country name"),
    country_id: Optional[int] = Query(None, description="Country ID"),
    competition_id: Optional[int] = Query(None, description="Competition ID"),
    competition_name: Optional[str] = Query(None, description="Competition name"),
    symbolic_name: Optional[str] = Query(None, description="Symbolic name"),
    name_for_url: Optional[str] = Query(None, description="URL-friendly name"),
    popularity_rank: Optional[int] = Query(None, description="Popularity rank"),
    color: Optional[str] = Query(None, description="Team primary color"),
    away_color: Optional[str] = Query(None, description="Team away color"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update a club from team selection.
    This endpoint is called after user selects a team.
    If no image URL is provided, generates one using 365scores image cache.
    """
    # Generate logo URL if not provided
    if not team_image_url:
        team_image_url = f"https://imagecache.365scores.com/image/upload/f_png,w_68,h_68,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/{team_id}"
    
    # Check if club already exists
    existing_club = db.query(Club).filter(Club.external_id == str(team_id)).first()
    
    if existing_club:
        # Update if needed
        existing_club.name = team_name
        existing_club.logo = team_image_url
        existing_club.country = country_name
        existing_club.country_id = str(country_id) if country_id else None
        existing_club.competition_id = str(competition_id) if competition_id else None
        existing_club.competition_name = competition_name
        existing_club.symbolic_name = symbolic_name
        existing_club.name_for_url = name_for_url
        existing_club.popularity_rank = popularity_rank
        existing_club.color = color
        existing_club.away_color = away_color
        db.commit()
        db.refresh(existing_club)
        return existing_club
    
    # Create new club
    club = Club(
        name=team_name,
        external_id=str(team_id),
        logo=team_image_url,
        country=country_name,
        country_id=str(country_id) if country_id else None,
        competition_id=str(competition_id) if competition_id else None,
        competition_name=competition_name,
        symbolic_name=symbolic_name,
        name_for_url=name_for_url,
        popularity_rank=popularity_rank,
        color=color,
        away_color=away_color
    )
    db.add(club)
    db.commit()
    db.refresh(club)
    return club


@router.get("", response_model=list[ClubOut])
def list_clubs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all clubs stored in the database."""
    clubs = db.query(Club).all()
    return clubs


@router.get("/{club_id}", response_model=ClubOut)
def get_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific club by ID."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    return club


@router.delete("/cache/clear")
def clear_cache(current_user: User = Depends(get_current_user)):
    """Clear all cached data. Useful after code changes."""
    import shutil
    try:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir(exist_ok=True)
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

