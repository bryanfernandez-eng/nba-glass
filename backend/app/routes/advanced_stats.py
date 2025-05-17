from fastapi import APIRouter, Query
from app.services import data_loader
from typing import List, Optional

router = APIRouter()

@router.get("/rankings/{stat}")
def get_player_rankings(
    stat: str, 
    season_id: Optional[str] = None, 
    min_games: int = Query(20, ge=1, description="Minimum games played to qualify")
):
    """
    Get player rankings for a specific statistic.
    
    Args:
        stat (str): The statistic to rank players by (e.g., 'PTS', 'REB', 'AST')
        season_id (Optional[str]): Filter by season ID (e.g., '2022-23')
        min_games (int): Minimum games played to qualify for rankings
        
    Returns:
        dict: List of players ranked by the specified statistic
    """
    rankings = data_loader.get_player_rankings(stat, season_id, min_games)
    
    return {
        "stat": stat,
        "season": season_id if season_id else "All Seasons",
        "min_games": min_games,
        "rankings": rankings
    }

@router.get("/compare")
def compare_players(player1: str, player2: str):
    """
    Compare statistics between two players.
    
    Args:
        player1 (str): First player's name
        player2 (str): Second player's name
        
    Returns:
        dict: Comparison of statistics between the two players
    """
    comparison = data_loader.compare_players(player1, player2)
    
    return comparison

@router.get("/search")
def search_players(q: str = Query(..., min_length=2, description="Search query")):
    """
    Search for players by name.
    
    Args:
        q (str): Search query string
        
    Returns:
        dict: List of players matching the search query
    """
    matching_players = data_loader.search_players(q)
    
    return {
        "query": q,
        "results": matching_players,
        "count": len(matching_players)
    }

@router.get("/players/efficiency")
def get_efficient_players(
    min_ppg: float = Query(10.0, ge=0.0, description="Minimum points per game"),
    min_games: int = Query(20, ge=1, description="Minimum games played"),
    season_id: Optional[str] = None
):
    """
    Get a list of efficient players based on true shooting percentage.
    
    Args:
        min_ppg (float): Minimum points per game to qualify
        min_games (int): Minimum games played to qualify
        season_id (Optional[str]): Filter by season ID
        
    Returns:
        dict: List of players ranked by true shooting percentage
    """
    # Get all players
    if season_id:
        players_data = data_loader.get_all_players_stats_year(int(season_id.split('-')[1]))
    else:
        players_data = data_loader.get_all_players_stats()
    
    # Process data
    player_efficiency = {}
    
    for entry in players_data:
        player_name = entry.get('PLAYER_NAME')
        if not player_name:
            continue
            
        games = entry.get('GP', 0)
        points = entry.get('PTS', 0)
        fga = entry.get('FGA', 0)
        fta = entry.get('FTA', 0)
        
        if games < min_games:
            continue
            
        ppg = points / games if games > 0 else 0
        
        if ppg < min_ppg:
            continue
            
        ts_pct = data_loader.calculate_true_shooting_percentage(points, fga, fta)
        
        if player_name not in player_efficiency:
            player_efficiency[player_name] = {
                'PLAYER_NAME': player_name,
                'TEAM': entry.get('TEAM_ABBREVIATION', ''),
                'GP': games,
                'PPG': round(ppg, 1),
                'TS%': ts_pct
            }
    
    # Convert to list and sort by TS%
    efficiency_list = list(player_efficiency.values())
    efficiency_list.sort(key=lambda x: x['TS%'], reverse=True)
    
    # Add ranking
    for i, player in enumerate(efficiency_list):
        player['RANK'] = i + 1
    
    return {
        "min_ppg": min_ppg,
        "min_games": min_games,
        "season": season_id if season_id else "All Seasons",
        "players": efficiency_list
    }

@router.get("/players/most_improved/{stat}")
def get_most_improved_players(
    stat: str,
    year1: int,
    year2: int,
    min_games: int = Query(20, ge=1, description="Minimum games played in both seasons")
):
    """
    Get players who improved the most in a specific statistic between two seasons.
    
    Args:
        stat (str): The statistic to measure improvement (e.g., 'PTS', 'REB', 'AST')
        year1 (int): First season year (ending year, e.g., 2022 for 2021-22)
        year2 (int): Second season year (ending year, e.g., 2023 for 2022-23)
        min_games (int): Minimum games played in both seasons
        
    Returns:
        dict: List of players ranked by improvement in the specified statistic
    """
    # Get data for both seasons
    try:
        season1_data = data_loader.get_all_players_stats_year(year1)
        season2_data = data_loader.get_all_players_stats_year(year2)
    except Exception:
        return {
            "error": f"Could not find data for one or both seasons: {year1-1}-{str(year1)[2:]} and {year2-1}-{str(year2)[2:]}"
        }
    
    # Prepare data for comparison
    stat = stat.upper()
    player_stats_year1 = {}
    player_stats_year2 = {}
    
    # Process first season
    for entry in season1_data:
        player_name = entry.get('PLAYER_NAME')
        if not player_name:
            continue
            
        games = entry.get('GP', 0)
        
        if games < min_games:
            continue
            
        if stat not in entry:
            continue
            
        stat_value = entry[stat]
        stat_per_game = stat_value / games if games > 0 else 0
        
        player_stats_year1[player_name] = {
            'PLAYER_NAME': player_name,
            'TEAM': entry.get('TEAM_ABBREVIATION', ''),
            'GP': games,
            f'{stat}_TOTAL': stat_value,
            f'{stat}_PER_GAME': round(stat_per_game, 2)
        }
    
    # Process second season
    for entry in season2_data:
        player_name = entry.get('PLAYER_NAME')
        if not player_name:
            continue
            
        games = entry.get('GP', 0)
        
        if games < min_games:
            continue
            
        if stat not in entry:
            continue
            
        stat_value = entry[stat]
        stat_per_game = stat_value / games if games > 0 else 0
        
        player_stats_year2[player_name] = {
            'PLAYER_NAME': player_name,
            'TEAM': entry.get('TEAM_ABBREVIATION', ''),
            'GP': games,
            f'{stat}_TOTAL': stat_value,
            f'{stat}_PER_GAME': round(stat_per_game, 2)
        }
    
    # Find players who played in both seasons and calculate improvement
    improved_players = []
    
    for player_name in player_stats_year1:
        if player_name in player_stats_year2:
            year1_stats = player_stats_year1[player_name]
            year2_stats = player_stats_year2[player_name]
            
            improvement = year2_stats[f'{stat}_PER_GAME'] - year1_stats[f'{stat}_PER_GAME']
            
            improved_players.append({
                'PLAYER_NAME': player_name,
                'YEAR1_TEAM': year1_stats['TEAM'],
                'YEAR2_TEAM': year2_stats['TEAM'],
                'YEAR1_GP': year1_stats['GP'],
                'YEAR2_GP': year2_stats['GP'],
                'YEAR1_STAT': year1_stats[f'{stat}_PER_GAME'],
                'YEAR2_STAT': year2_stats[f'{stat}_PER_GAME'],
                'IMPROVEMENT': round(improvement, 2)
            })
    
    # Sort by improvement (descending)
    improved_players.sort(key=lambda x: x['IMPROVEMENT'], reverse=True)
    
    # Add ranking
    for i, player in enumerate(improved_players):
        player['RANK'] = i + 1
    
    return {
        "stat": stat,
        "season1": f"{year1-1}-{str(year1)[2:]}",
        "season2": f"{year2-1}-{str(year2)[2:]}",
        "min_games": min_games,
        "players": improved_players
    }