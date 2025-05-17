import pandas as pd 
import os 
import logging
from app.utils.error_handler import NotFoundError, DataProcessingError

logger = logging.getLogger("nba_api.data_loader")

# Define path to data file
csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "nba_regular_season_totals.csv")

try:
    regular_season_df = pd.read_csv(csv_path)
    logger.info(f"Successfully loaded NBA data from {csv_path}")
except Exception as e:
    logger.error(f"Failed to load NBA data: {str(e)}")
    # Create an empty DataFrame with the expected columns to avoid breaking the app
    regular_season_df = pd.DataFrame(columns=[
        'PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 
        'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 
        'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 
        'BLK', 'TOV', 'PF', 'PTS', 'PLAYER_NAME'
    ])
    raise DataProcessingError(f"Failed to load NBA data: {str(e)}")

# Cache for player name normalization
player_name_cache = {}

def normalize_player_name(name: str) -> str:
    """Normalize player name for consistent lookup."""
    if name in player_name_cache:
        return player_name_cache[name]
    
    normalized = name.lower().replace(" ", "")
    player_name_cache[name] = normalized
    return normalized

def get_all_players(): 
    """Get list of all players in the dataset."""
    try:
        return regular_season_df['PLAYER_NAME'].unique().tolist()
    except Exception as e:
        logger.error(f"Error getting all players: {str(e)}")
        raise DataProcessingError(f"Error retrieving player list: {str(e)}")

def find_player(player_name: str):
    """Find a player by name with error handling."""
    try:
        normalized_name = normalize_player_name(player_name)
        player_stats = regular_season_df[
            regular_season_df['PLAYER_NAME'].str.lower().str.replace(" ", "") == normalized_name
        ]
        
        if player_stats.empty:
            # Try partial matching if exact match fails
            all_players = regular_season_df['PLAYER_NAME'].unique()
            possible_matches = [
                p for p in all_players 
                if normalized_name in normalize_player_name(p)
            ]
            
            if possible_matches:
                logger.info(f"No exact match for '{player_name}', found similar: {possible_matches}")
                return None, possible_matches
            else:
                logger.warning(f"No player found matching '{player_name}'")
                return None, []
        
        return player_stats, []
    except Exception as e:
        logger.error(f"Error finding player '{player_name}': {str(e)}")
        raise DataProcessingError(f"Error searching for player: {str(e)}")

def get_player_stats(player_name: str): 
    """Get player stats with error handling."""
    player_stats, similar_players = find_player(player_name)
    
    if player_stats is None:
        if similar_players:
            raise NotFoundError("Player", player_name, f"Did you mean one of these? {', '.join(similar_players[:5])}")
        raise NotFoundError("Player", player_name)
    
    try:
        player_stats = player_stats.drop(columns=['PLAYER_NAME'])
        return player_stats.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error processing stats for player '{player_name}': {str(e)}")
        raise DataProcessingError(f"Error processing player statistics: {str(e)}")

def get_player_career_stats(player_name: str): 
    """Get player career stats with error handling."""
    player_stats, similar_players = find_player(player_name)
    
    if player_stats is None:
        if similar_players:
            raise NotFoundError("Player", player_name, f"Did you mean one of these? {', '.join(similar_players[:5])}")
        raise NotFoundError("Player", player_name)
    
    try:
        total_gp = player_stats['GP'].sum()
        if total_gp == 0:
            total_gp = 1  
        
        total_gs = player_stats['GS'].sum()
        total_min = player_stats['MIN'].sum()
        total_pts = player_stats['PTS'].sum()
        total_reb = player_stats['REB'].sum()   
        total_ast = player_stats['AST'].sum()
        total_stl = player_stats['STL'].sum()
        total_blk = player_stats['BLK'].sum()
        total_tov = player_stats['TOV'].sum()
        total_fg_made = player_stats['FGM'].sum()
        total_fg_att = player_stats['FGA'].sum()
        total_fg_pct = round((total_fg_made / total_fg_att) * 100, 1) if total_fg_att > 0 else 0
        total_3p_made = player_stats['FG3M'].sum()
        total_3p_att = player_stats['FG3A'].sum()
        total_3p_pct = round((total_3p_made / total_3p_att) * 100, 1) if total_3p_att > 0 else 0
        total_ft_made = player_stats['FTM'].sum()
        total_ft_att = player_stats['FTA'].sum()
        total_ft_pct = round((total_ft_made / total_ft_att) * 100, 1) if total_ft_att > 0 else 0
        total_oreb = player_stats['OREB'].sum()
        total_dreb = player_stats['DREB'].sum()
        total_pf = player_stats['PF'].sum()
        
        # Calculate advanced stats
        true_shooting_pct = calculate_true_shooting_percentage(total_pts, total_fg_att, total_ft_att)
        per = calculate_player_efficiency_rating(
            player_stats, total_min, total_fg_made, total_fg_att, 
            total_ft_made, total_ft_att, total_3p_made, total_oreb, 
            total_dreb, total_ast, total_stl, total_blk, total_pf, total_tov
        )
        
        career_averages = {
            "PPG": round(total_pts / total_gp, 2),
            "RPG": round(total_reb / total_gp, 2),
            "APG": round(total_ast / total_gp, 2),
            "SPG": round(total_stl / total_gp, 2),
            "BPG": round(total_blk / total_gp, 2),
            "TPG": round(total_tov / total_gp, 2),
            "FGAPG": round(total_fg_att / total_gp, 2),
            "FGMPG": round(total_fg_made / total_gp, 2),
            "3PAPG": round(total_3p_att / total_gp, 2),
            "3PMPG": round(total_3p_made / total_gp, 2),
            "FTAPG": round(total_ft_att / total_gp, 2),
            "FTMPG": round(total_ft_made / total_gp, 2),
            "OREBPG": round(total_oreb / total_gp, 2),
            "DREBPG": round(total_dreb / total_gp, 2),
            "FPG": round(total_pf / total_gp, 2),
            "FG%": total_fg_pct,
            "3P%": total_3p_pct,
            "FT%": total_ft_pct,
            "TS%": true_shooting_pct,
            "PER": per
        }
        
        return {
            "career_totals": {
                "GP": int(total_gp),
                "GS": int(total_gs),
                "MIN": int(total_min),
                "PTS": int(total_pts),
                "REB": int(total_reb),
                "AST": int(total_ast),
                "STL": int(total_stl),
                "BLK": int(total_blk),
                "TOV": int(total_tov),
                "FGM": int(total_fg_made),
                "FGA": int(total_fg_att),
                "FG%": total_fg_pct,
                "3PM": int(total_3p_made),
                "3PA": int(total_3p_att),
                "3P%": total_3p_pct,
                "FTM": int(total_ft_made),
                "FTA": int(total_ft_att),
                "FT%": total_ft_pct,
                "OREB": int(total_oreb),
                "DREB": int(total_dreb),
                "PF": int(total_pf)
            },
            "career_averages": career_averages,
            "advanced_stats": {
                "TS%": true_shooting_pct,
                "PER": per
            }
        }
    except Exception as e:
        logger.error(f"Error calculating career stats for '{player_name}': {str(e)}")
        raise DataProcessingError(f"Error calculating career statistics: {str(e)}")
    
def get_player_seasons(player_name: str): 
    """Get player seasons with error handling."""
    player_stats, similar_players = find_player(player_name)
    
    if player_stats is None:
        if similar_players:
            raise NotFoundError("Player", player_name, f"Did you mean one of these? {', '.join(similar_players[:5])}")
        raise NotFoundError("Player", player_name)
        
    try:
        seasons = player_stats['SEASON_ID'].unique().tolist()
        return seasons
    except Exception as e:
        logger.error(f"Error retrieving seasons for '{player_name}': {str(e)}")
        raise DataProcessingError(f"Error retrieving player seasons: {str(e)}")

def get_player_stat_trend(player_name: str, stat: str): 
    """Get player stat trends with error handling."""
    stat = stat.upper()
    player_stats, similar_players = find_player(player_name)
    
    if player_stats is None:
        if similar_players:
            raise NotFoundError("Player", player_name, f"Did you mean one of these? {', '.join(similar_players[:5])}")
        raise NotFoundError("Player", player_name)
    
    try:
        if stat not in player_stats.columns: 
            logger.warning(f"Stat '{stat}' not found in player stats.")
            valid_stats = [col for col in player_stats.columns if col not in ['PLAYER_ID', 'LEAGUE_ID', 'TEAM_ID']]
            raise NotFoundError("Statistic", stat, f"Valid statistics: {', '.join(valid_stats[:10])}...")
        
        trend = player_stats[['SEASON_ID', stat]].copy()
        trend = trend.rename(columns={stat: "value"})
        trend['SEASON_ID'] = trend['SEASON_ID'].astype(str)
        
        return trend.to_dict(orient='records')
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stat trend for '{player_name}': {str(e)}")
        raise DataProcessingError(f"Error retrieving player stat trend: {str(e)}")

def get_all_players_stats(): 
    """Get all players stats with error handling."""
    try:
        return regular_season_df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error retrieving all player stats: {str(e)}")
        raise DataProcessingError(f"Error retrieving all player statistics: {str(e)}")

def get_all_players_stats_year(year: int): 
    """Get all players stats by year with error handling."""
    try:
        selected_year = f"{year-1}-{str(year)[2:]}"
        year_stats = regular_season_df[regular_season_df['SEASON_ID'] == selected_year]
        
        if year_stats.empty: 
            raise NotFoundError("Season", str(year))
        
        return year_stats.to_dict(orient='records')
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stats for year {year}: {str(e)}")
        raise DataProcessingError(f"Error retrieving statistics for year {year}: {str(e)}")

# New functions for advanced statistics

def calculate_true_shooting_percentage(pts, fga, fta):
    """Calculate true shooting percentage."""
    try:
        if fga == 0 and fta == 0:
            return 0
        return round((pts / (2 * (fga + 0.44 * fta))) * 100, 1)
    except Exception:
        return 0

def calculate_player_efficiency_rating(player_data, min_played, fgm, fga, ftm, fta, fg3m, oreb, dreb, ast, stl, blk, pf, tov):
    """Calculate a simplified version of Player Efficiency Rating (PER)."""
    try:
        if min_played == 0:
            return 0
            
        # Simplified PER calculation
        per = (fgm * 2.35 + fg3m * 0.5 + ftm * 0.5 + ast * 0.5 + stl * 0.5 + 
               blk * 0.5 + oreb * 0.4 + dreb * 0.3 - pf * 0.5 - tov) / (min_played / 48)
        
        return round(per, 1)
    except Exception:
        return 0

def get_team_players(team_abbreviation: str):
    """Get all players for a specific team."""
    try:
        team_abbreviation = team_abbreviation.upper()
        team_players_data = regular_season_df[regular_season_df['TEAM_ABBREVIATION'] == team_abbreviation]
        
        if team_players_data.empty:
            # Find all available teams for suggestion
            available_teams = regular_season_df['TEAM_ABBREVIATION'].unique().tolist()
            raise NotFoundError("Team", team_abbreviation, f"Available teams: {', '.join(available_teams)}")
            
        unique_players = team_players_data['PLAYER_NAME'].unique().tolist()
        return unique_players
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving players for team {team_abbreviation}: {str(e)}")
        raise DataProcessingError(f"Error retrieving team players: {str(e)}")

def get_all_teams():
    """Get all NBA teams in the dataset."""
    try:
        return regular_season_df['TEAM_ABBREVIATION'].unique().tolist()
    except Exception as e:
        logger.error(f"Error retrieving teams: {str(e)}")
        raise DataProcessingError(f"Error retrieving team list: {str(e)}")

def get_team_stats(team_abbreviation: str):
    """Get team statistics aggregated from player data."""
    try:
        team_abbreviation = team_abbreviation.upper()
        team_data = regular_season_df[regular_season_df['TEAM_ABBREVIATION'] == team_abbreviation]
        
        if team_data.empty:
            available_teams = regular_season_df['TEAM_ABBREVIATION'].unique().tolist()
            raise NotFoundError("Team", team_abbreviation, f"Available teams: {', '.join(available_teams)}")
        
        # Group by season and aggregate
        team_stats_by_season = team_data.groupby('SEASON_ID').agg({
            'GP': 'first',  # Games in a season
            'MIN': 'sum',
            'FGM': 'sum',
            'FGA': 'sum',
            'FG3M': 'sum',
            'FG3A': 'sum',
            'FTM': 'sum',
            'FTA': 'sum',
            'OREB': 'sum',
            'DREB': 'sum',
            'REB': 'sum',
            'AST': 'sum',
            'STL': 'sum',
            'BLK': 'sum',
            'TOV': 'sum',
            'PF': 'sum',
            'PTS': 'sum',
            'PLAYER_NAME': 'nunique'  # Count unique players
        }).reset_index()
        
        # Rename the count of players column
        team_stats_by_season = team_stats_by_season.rename(columns={'PLAYER_NAME': 'NUM_PLAYERS'})
        
        # Calculate percentages
        team_stats_by_season['FG_PCT'] = (team_stats_by_season['FGM'] / team_stats_by_season['FGA'] * 100).round(1)
        team_stats_by_season['FG3_PCT'] = (team_stats_by_season['FG3M'] / team_stats_by_season['FG3A'] * 100).round(1)
        team_stats_by_season['FT_PCT'] = (team_stats_by_season['FTM'] / team_stats_by_season['FTA'] * 100).round(1)
        
        # Add team abbreviation
        team_stats_by_season['TEAM_ABBREVIATION'] = team_abbreviation
        
        return team_stats_by_season.to_dict(orient='records')
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stats for team {team_abbreviation}: {str(e)}")
        raise DataProcessingError(f"Error retrieving team statistics: {str(e)}")

def compare_players(player1_name: str, player2_name: str):
    """Compare statistics between two players."""
    player1_stats, similar_players1 = find_player(player1_name)
    player2_stats, similar_players2 = find_player(player2_name)
    
    if player1_stats is None:
        if similar_players1:
            raise NotFoundError("Player", player1_name, f"Did you mean one of these? {', '.join(similar_players1[:5])}")
        raise NotFoundError("Player", player1_name)
        
    if player2_stats is None:
        if similar_players2:
            raise NotFoundError("Player", player2_name, f"Did you mean one of these? {', '.join(similar_players2[:5])}")
        raise NotFoundError("Player", player2_name)
    
    try:
        # Get career stats for both players
        player1_career = get_player_career_stats(player1_name)
        player2_career = get_player_career_stats(player2_name)
        
        # Create comparison dictionary
        comparison = {
            "player1_name": player1_name,
            "player2_name": player2_name,
            "career_totals_comparison": {
                stat: {
                    "player1": player1_career["career_totals"][stat],
                    "player2": player2_career["career_totals"][stat],
                    "difference": player1_career["career_totals"][stat] - player2_career["career_totals"][stat]
                } for stat in player1_career["career_totals"]
            },
            "career_averages_comparison": {
                stat: {
                    "player1": player1_career["career_averages"][stat],
                    "player2": player2_career["career_averages"][stat],
                    "difference": player1_career["career_averages"][stat] - player2_career["career_averages"][stat]
                } for stat in player1_career["career_averages"]
            }
        }
        
        return comparison
    except Exception as e:
        logger.error(f"Error comparing players '{player1_name}' and '{player2_name}': {str(e)}")
        raise DataProcessingError(f"Error comparing players: {str(e)}")

def get_player_rankings(stat: str, season_id: str = None, min_games: int = 20):
    """Get player rankings for a specific statistic."""
    try:
        stat = stat.upper()
        
        # Validate the statistic exists
        if stat not in regular_season_df.columns:
            valid_stats = [col for col in regular_season_df.columns if col not in ['PLAYER_ID', 'LEAGUE_ID', 'TEAM_ID']]
            raise NotFoundError("Statistic", stat, f"Valid statistics: {', '.join(valid_stats[:10])}...")
        
        # Filter by season if provided
        if season_id:
            filtered_df = regular_season_df[regular_season_df['SEASON_ID'] == season_id]
            if filtered_df.empty:
                all_seasons = regular_season_df['SEASON_ID'].unique().tolist()
                raise NotFoundError("Season", season_id, f"Available seasons: {', '.join(all_seasons[:10])}...")
        else:
            filtered_df = regular_season_df
        
        # Filter by minimum games
        filtered_df = filtered_df[filtered_df['GP'] >= min_games]
        
        if filtered_df.empty:
            raise NotFoundError("Players", f"with min {min_games} games")
        
        # Group by player and calculate average per game
        if stat in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
            # For percentages, we don't need per-game calculation
            player_stats = filtered_df.groupby('PLAYER_NAME')[stat].mean().reset_index()
            player_stats = player_stats.sort_values(by=stat, ascending=False)
        else:
            # For counting stats, calculate per-game average
            player_stats = filtered_df.groupby('PLAYER_NAME').agg({
                stat: 'sum',
                'GP': 'sum',
                'TEAM_ABBREVIATION': lambda x: ', '.join(set(x))
            }).reset_index()
            
            player_stats[f'{stat}_PER_GAME'] = (player_stats[stat] / player_stats['GP']).round(2)
            player_stats = player_stats.sort_values(by=f'{stat}_PER_GAME', ascending=False)
            # Rename for consistency in output
            player_stats = player_stats.rename(columns={f'{stat}_PER_GAME': 'VALUE'})
        
        # Add rank column
        player_stats['RANK'] = range(1, len(player_stats) + 1)
        
        # Keep only necessary columns
        if 'VALUE' in player_stats.columns:
            result_df = player_stats[['RANK', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'VALUE', 'GP']]
        else:
            player_stats = player_stats.rename(columns={stat: 'VALUE'})
            result_df = player_stats[['RANK', 'PLAYER_NAME', 'VALUE']]
            
        return result_df.to_dict(orient='records')
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rankings for '{stat}': {str(e)}")
        raise DataProcessingError(f"Error retrieving player rankings: {str(e)}")

def search_players(query: str):
    """Search for players by name."""
    try:
        query = query.lower()
        matching_players = [
            player for player in regular_season_df['PLAYER_NAME'].unique()
            if query in player.lower()
        ]
        
        if not matching_players:
            raise NotFoundError("Player", query)
            
        return matching_players
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error searching for players with query '{query}': {str(e)}")
        raise DataProcessingError(f"Error searching for players: {str(e)}")