from fastapi import APIRouter, Query, Path
from app.services import data_loader
from typing import List, Optional

router = APIRouter()

@router.get("/players")
def get_players(
    order: str = Query("asc", description="Sort order (asc or desc)"),
    limit: int = Query(None, ge=1, description="Limit the number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
): 
    """
    Get a list of all players.
    
    Args:
        order (str): Sort order - "asc" for ascending, "desc" for descending
        limit (int): Maximum number of players to return
        offset (int): Number of players to skip for pagination
        
    Returns:
        dict: List of player names
    """
    player_list = data_loader.get_all_players()
    
    if order.lower() == "desc":
        sorted_player_list = sorted(player_list, reverse=True)
    else:
        sorted_player_list = sorted(player_list)
    
    # Apply pagination if limit is specified
    if limit is not None:
        paginated_players = sorted_player_list[offset:offset + limit]
    else:
        paginated_players = sorted_player_list[offset:]
    
    return {
        "players": paginated_players, 
        "count": len(paginated_players),
        "total": len(player_list),
        "offset": offset,
        "limit": limit
    }

@router.get("/players/{player_name}/stats")
def get_player_stats(
    player_name: str = Path(..., description="Player name (case-insensitive)"),
    season_id: Optional[str] = Query(None, description="Filter by season ID (e.g., '2022-23')")
): 
    """
    Get a player's statistics.
    
    Args:
        player_name (str): Player name
        season_id (Optional[str]): Filter by season ID
        
    Returns:
        dict: Player statistics
    """
    player_stats = data_loader.get_player_stats(player_name)
    
    # Filter by season if provided
    if season_id and player_stats:
        player_stats = [stat for stat in player_stats if stat['SEASON_ID'] == season_id]
        
        if not player_stats:
            return {
                "player_name": player_name,
                "error": f"No data found for season {season_id}",
                "available_seasons": data_loader.get_player_seasons(player_name)
            }
    
    return {
        "player_name": player_name, 
        "stats": player_stats, 
        "count": len(player_stats) if player_stats else 0
    }

@router.get("/players/{player_name}/career_stats")
def get_player_career_stats(
    player_name: str = Path(..., description="Player name (case-insensitive)")
):
    """
    Get a player's career statistics totals and averages.
    
    Args:
        player_name (str): Player name
        
    Returns:
        dict: Player career statistics
    """
    player_career_stats = data_loader.get_player_career_stats(player_name)
    
    return {
        "player_name": player_name, 
        "career_stats": player_career_stats
    }

@router.get("/players/{player_name}/seasons")
def get_player_seasons(
    player_name: str = Path(..., description="Player name (case-insensitive)")
):
    """
    Get a list of seasons a player has played.
    
    Args:
        player_name (str): Player name
        
    Returns:
        dict: List of seasons
    """
    player_seasons = data_loader.get_player_seasons(player_name)
    
    return {
        "player_name": player_name, 
        "seasons": player_seasons, 
        "count": len(player_seasons)
    }

@router.get("/players/{player_name}/stat_trend/{stat}")
def get_player_stat_trend(
    player_name: str = Path(..., description="Player name (case-insensitive)"),
    stat: str = Path(..., description="Statistic to track (e.g., 'PTS', 'REB', 'AST')")
):
    """
    Get the trend of a specific statistic for a player over seasons.
    
    Args:
        player_name (str): Player name
        stat (str): Statistic to track
        
    Returns:
        dict: Trend data for the specified statistic
    """
    player_stat_trend = data_loader.get_player_stat_trend(player_name, stat)
    
    return {
        "player_name": player_name, 
        "stat": stat,
        "stat_trend": player_stat_trend, 
        "count": len(player_stat_trend) if player_stat_trend else 0
    }

@router.get("/players/stats")
def get_all_players_stats(
    limit: int = Query(100, ge=1, description="Limit the number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get statistics for all players.
    
    Args:
        limit (int): Maximum number of players to return
        offset (int): Number of players to skip for pagination
        
    Returns:
        dict: Statistics for all players
    """
    all_players_stats = data_loader.get_all_players_stats()
    
    # Apply pagination
    paginated_stats = all_players_stats[offset:offset + limit]
    
    return {
        "players": paginated_stats, 
        "count": len(paginated_stats),
        "total": len(all_players_stats),
        "offset": offset,
        "limit": limit
    }

@router.get("/players/stats/{year}")
def get_all_players_stats_year(
    year: int = Path(..., description="Season ending year (e.g., 2023 for 2022-23 season)"),
    limit: int = Query(100, ge=1, description="Limit the number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
): 
    """
    Get statistics for all players in a specific season.
    
    Args:
        year (int): Season ending year
        limit (int): Maximum number of players to return
        offset (int): Number of players to skip for pagination
        
    Returns:
        dict: Statistics for all players in the specified season
    """
    all_players_stats_year = data_loader.get_all_players_stats_year(year)
    
    # Apply pagination
    paginated_stats = all_players_stats_year[offset:offset + limit]
    
    return {
        "season": f"{year-1}-{str(year)[2:]}",
        "players": paginated_stats, 
        "count": len(paginated_stats),
        "total": len(all_players_stats_year),
        "offset": offset,
        "limit": limit
    }

@router.get("/players/stats/leaders/{stat}")
def get_stat_leaders(
    stat: str = Path(..., description="Statistic to get leaders for (e.g., 'PTS', 'REB', 'AST')"),
    season_id: Optional[str] = Query(None, description="Filter by season ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of leaders to return")
):
    """
    Get the leaders in a specific statistical category.
    
    Args:
        stat (str): Statistic to get leaders for
        season_id (Optional[str]): Filter by season ID
        limit (int): Number of leaders to return
        
    Returns:
        dict: List of statistical leaders
    """
    # Using the rankings endpoint from advanced_stats
    rankings = data_loader.get_player_rankings(stat, season_id, min_games=20)
    
    # Limit the results
    limited_rankings = rankings[:limit]
    
    return {
        "stat": stat,
        "season": season_id if season_id else "All Seasons",
        "leaders": limited_rankings,
        "count": len(limited_rankings)
    }