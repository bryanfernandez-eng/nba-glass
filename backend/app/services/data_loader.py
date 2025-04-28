import pandas as pd 
import os 

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "nba_regular_season_totals.csv")
regular_season_df = pd.read_csv(csv_path)


def get_all_players(): 
    print(regular_season_df)
    return regular_season_df['PLAYER_NAME'].unique().tolist()

def get_player_stats(player_name: str): 
    player_stats = regular_season_df[regular_season_df['PLAYER_NAME'].str.lower().str.replace(" ", "") == player_name.lower().replace(" ", "")]
    player_stats = player_stats.drop(columns=['PLAYER_NAME'])
    print(player_stats)
    if player_stats.empty: 
        return None
    return player_stats.to_dict(orient='records')

def get_player_career_stats(player_name: str): 
    player_stats = regular_season_df[
        regular_season_df['PLAYER_NAME'].str.lower().str.replace(" ", "") == player_name.lower().replace(" ", "")
    ]

    if player_stats.empty: 
        return None
    
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
        "FT%": total_ft_pct
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
        "career_averages": career_averages
    }
    
    
def get_player_seasons(player_name: str): 
    player_stats = regular_season_df[
        regular_season_df['PLAYER_NAME'].str.lower().str.replace(" ", "") == player_name.lower().replace(" ", "")
    ]
    
    if player_stats.empty: 
        return None
        
    seasons = player_stats['SEASON_ID'].unique().tolist()
    return seasons

def get_player_stat_trend(player_name: str, stat: str): 


    stat = stat.upper()
    player_stats = regular_season_df[
        regular_season_df['PLAYER_NAME'].str.lower().str.replace(" ", "") == player_name.lower().replace(" ", "")
    ]
    print()
    if stat not in player_stats.columns: 
        print(f"Stat '{stat}' not found in player stats.")
        return None    
    if player_stats.empty: 
        return None
    
    trend = player_stats[['SEASON_ID', stat]].copy()
    trend = trend.rename(columns={stat: "value"})
    trend['SEASON_ID'] = trend['SEASON_ID'].astype(str)
    
    return trend.to_dict(orient='records')