from fastapi import APIRouter 
from app.services import data_loader 

router = APIRouter()

# gets all players 
@router.get("/players")
def get_players(order: str = "asc"): 
    player_list = data_loader.get_all_players()
    if order == "desc":
        sorted_player_list = sorted(player_list, reverse=True)
    else:
        sorted_player_list = sorted(player_list)
    return {"players": sorted_player_list, "count": len(sorted_player_list)}

# get players stats by season 
@router.get("/players/{player_name}/stats")
def get_players_stats(player_name: str): 
    player_stats = data_loader.get_player_stats(player_name)
    if player_stats is None: 
        return {"error": "Player not found"}
    return {"player_name": player_name, "stats": player_stats, "count": len(player_stats)}

# get career stats totals and averages 
@router.get("/players/{player_name}/career_stats")
def get_players_career_stats(player_name: str):
    player_career_stats = data_loader.get_player_career_stats(player_name)
    if player_career_stats is None: 
        return {"error": "Player not found"}
    return {"player_name": player_name, "career_stats": player_career_stats}


# get players seasons
@router.get("/players/{player_name}/seasons")
def get_players_seasons(player_name: str):
    player_seasons = data_loader.get_player_seasons(player_name)
    if player_seasons is None: 
        return {"error": "Player not found"}
    return {"player_name": player_name, "seasons": player_seasons, "count": len(player_seasons)}

# get players stat trend
@router.get("/players/{player_name}/stat_trend/{stat}")
def get_players_stat_trend(player_name: str, stat: str):
    player_stat_trend = data_loader.get_player_stat_trend(player_name, stat)
    if player_stat_trend is None: 
        return {"error": "Player not found"}
    return {"player_name": player_name, "stat_trend": player_stat_trend, "count": len(player_stat_trend)}

# get all players stats 
@router.get("/players/stats")
def get_all_players_stats():
    all_players_stats = data_loader.get_all_players_stats()
    if all_players_stats is None: 
        return {"error": "No players found"}
    return {"players": all_players_stats, "count": len(all_players_stats)}

# get all players stats by year
@router.get("/players/stats/{year}")
def get_all_players_stats_year(year: int): 
    all_players_stats_year = data_loader.get_all_players_stats_year(year)
    if not all_players_stats_year: 
        return {"error": "No players found"}
    return {"players": all_players_stats_year, "count": len(all_players_stats_year)}