import pandas as pd
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from tqdm import tqdm
from datetime import datetime
import os

# Get all active players
all_players = players.get_players()
active_players = [player for player in all_players if player['is_active']]

regular_season_totals = []

# Loop through active players with progress bar
for player in tqdm(active_players, desc="Fetching Player Stats"):
    try:
        career = playercareerstats.PlayerCareerStats(
            player_id=player['id'],
            per_mode36='Totals'
        )
        dfs = career.get_data_frames()

        reg_total = dfs[0]

        # Skip if DataFrame is empty (player hasn't played yet)
        if reg_total.empty:
            continue

        # Add player name for reference
        reg_total['PLAYER_NAME'] = player['full_name']

        regular_season_totals.append(reg_total)

        time.sleep(0.6)  # Respect API rate limits
    except Exception as e:
        print(f"Error fetching data for {player['full_name']}: {e}")
        continue  # Skip players with issues

# Check if there's data to save
if regular_season_totals:
    # Combine all non-empty DataFrames
    regular_df = pd.concat(regular_season_totals, ignore_index=True)

    # Define absolute path to /app/data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(base_dir, '..', 'app', 'data')

    # Create the folder if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)

    # Save CSV
    csv_path = os.path.join(data_folder, f'nba_regular_season_totals.csv')
    regular_df.to_csv(csv_path, index=False)

    print(f"Data collection complete! Saved to: {csv_path}")
else:
    print("No data collected. All players may have empty stats.")
