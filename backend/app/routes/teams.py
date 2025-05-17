from fastapi import APIRouter, Query
from app.services import data_loader
from typing import List, Optional

router = APIRouter()

@router.get("/teams", response_model=List[str])
def get_all_teams():
    """
    Get a list of all NBA teams in the dataset.
    
    Returns:
        List[str]: A list of team abbreviations
    """
    teams = data_loader.get_all_teams()
    return teams

@router.get("/teams/{team_abbreviation}")
def get_team_stats(team_abbreviation: str):
    """
    Get team statistics aggregated from player data.
    
    Args:
        team_abbreviation (str): The team abbreviation (e.g., 'LAL', 'BOS')
        
    Returns:
        dict: Team statistics by season
    """
    team_stats = data_loader.get_team_stats(team_abbreviation)
    return {
        "team": team_abbreviation,
        "stats": team_stats
    }

@router.get("/teams/{team_abbreviation}/players")
def get_team_players(team_abbreviation: str):
    """
    Get all players that have played for a specific team.
    
    Args:
        team_abbreviation (str): The team abbreviation (e.g., 'LAL', 'BOS')
        
    Returns:
        dict: List of players who have played for the team
    """
    players = data_loader.get_team_players(team_abbreviation)
    return {
        "team": team_abbreviation,
        "players": players,
        "count": len(players)
    }

@router.get("/teams/{team_abbreviation}/seasons/{season_id}")
def get_team_season_stats(team_abbreviation: str, season_id: str):
    """
    Get team statistics for a specific season.
    
    Args:
        team_abbreviation (str): The team abbreviation (e.g., 'LAL', 'BOS')
        season_id (str): The season ID (e.g., '2022-23')
        
    Returns:
        dict: Team statistics for the specified season
    """
    team_stats = data_loader.get_team_stats(team_abbreviation)
    season_stats = [stat for stat in team_stats if stat['SEASON_ID'] == season_id]
    
    if not season_stats:
        available_seasons = [stat['SEASON_ID'] for stat in team_stats]
        return {
            "error": f"No data found for {team_abbreviation} in season {season_id}",
            "available_seasons": available_seasons
        }
    
    return {
        "team": team_abbreviation,
        "season": season_id,
        "stats": season_stats[0]
    }