import pandas as pd
import logging
import os
from etl.extract import extract_data


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def transform_matches(matches_df):
    """
    Here we are doing data cleaning 
    """
    
    logging.info("Starting matches transformation...")
    
    df = matches_df.copy()
    
    #fixing date column  and also extracting month and year 
    
    df['date']=pd.to_datetime(df['date'])
    df['year']=df['date'].dt.year
    df['month']=df['date'].dt.month
    df['month_name']=df['date'].dt.strftime('%B')
    
    logging.info("✓ Date column fixed and year/month extracted")
    
      # ── 2. FIX TEAM NAMES ───────────────────────────────────────
    # Teams changed names over the years - standardize them
    team_name_fixes = {
        'Delhi Daredevils'            : 'Delhi Capitals',
        'Deccan Chargers'             : 'Sunrisers Hyderabad',
        'Kings XI Punjab'             : 'Punjab Kings',
        'Pune Warriors'               : 'Rising Pune Supergiants',
        'Royal Challengers Bangalore'  : 'Royal Challengers Bengaluru',
        'Rising Pune Supergiant'       : 'Rising Pune Supergiants'
    }
    
    df['team1']        = df['team1'].replace(team_name_fixes)
    df['team2']        = df['team2'].replace(team_name_fixes)
    df['winner']       = df['winner'].replace(team_name_fixes)
    df['toss_winner']  = df['toss_winner'].replace(team_name_fixes)
    logging.info("✓ Team names standardized means changed successfully")
    
    
    # lets handle all the null values 
    
    null_before = df.isnull().sum().sum()
    df['city']             = df['city'].fillna('Unknown')
    df['player_of_match']  = df['player_of_match'].fillna('Unknown')
    df['winner']           = df['winner'].fillna('No Result')
    df['result_margin']    = df['result_margin'].fillna(0)
    df['method']           = df['method'].fillna('Normal')
    df['target_runs']      = df['target_runs'].fillna(0)
    df['target_overs']     = df['target_overs'].fillna(20)
    
    null_after = df.isnull().sum().sum()
    logging.info(f"✓ Nulls fixed: {null_before} → {null_after}")
    
    
    # Did toss winner win the match?
    df['toss_match_winner'] = df['toss_winner'] == df['winner']
    
    # Was it a close match or dominant win?
    def classify_win(row):
        if row['result'] == 'runs':
            if row['result_margin'] <= 10:
                return 'Close'
            elif row['result_margin'] <= 30:
                return 'Comfortable'
            else:
                return 'Dominant'
        elif row['result'] == 'wickets':
            if row['result_margin'] <= 2:
                return 'Close'
            elif row['result_margin'] <= 5:
                return 'Comfortable'
            else:
                return 'Dominant'
        else:
            return 'No Result'
        
        
    df['win_type'] = df.apply(classify_win, axis=1)
    logging.info("✓ Added toss impact and win type columns")
    
    
    logging.info(f"Matches transformation complete! Final shape: {df.shape}")
    return df   
        
    
def transform_deliveries(deliveries_df):
    """
    Cleaning and transformation of Deliveries data
    """
    logging.info("Deliveries Transformation started ")
    df = deliveries_df.copy()
    #handling Null values
    null_before = df.isnull().sum().sum()
    
    df['extras_type']      = df['extras_type'].fillna('none')
    df['player_dismissed'] = df['player_dismissed'].fillna('not_out')
    df['dismissal_kind']   = df['dismissal_kind'].fillna('not_out')
    df['fielder']          = df['fielder'].fillna('none')
    
    null_after = df.isnull().sum().sum()
    logging.info(f"✓ Nulls fixed: {null_before} → {null_after}")
    
    # ── 2. FIX TEAM NAMES (same as matches) ────────────────────
    team_name_fixes = {
        'Delhi Daredevils'            : 'Delhi Capitals',
        'Deccan Chargers'             : 'Sunrisers Hyderabad',
        'Kings XI Punjab'             : 'Punjab Kings',
        'Pune Warriors'               : 'Rising Pune Supergiants',
        'Royal Challengers Bangalore' : 'Royal Challengers Bengaluru',
        'Rising Pune Supergiant'      : 'Rising Pune Supergiants'
    }
    
    df['batting_team']  = df['batting_team'].replace(team_name_fixes)
    df['bowling_team']  = df['bowling_team'].replace(team_name_fixes)
    logging.info("✓ Team names standardized in deliveries")
    
    # ── 3. ADD USEFUL COLUMNS ───────────────────────────────────
    # Is this a boundary?
    df['is_four'] = df['batsman_runs'] == 4
    df['is_six']  = df['batsman_runs'] == 6
    df['is_legbye'] = df['extras_type']=="legbyes"
    df['is_wide'] = df['extras_type']=="wides"
    df['is_Noball']=df['extras_type']=="noballs"
    df['is_dot_ball'] = df['total_runs'] == 0
    
    
    # Phase of the game
    def get_phase(over):
        if over <= 6:
            return 'Powerplay'
        elif over <= 15:
            return 'Middle'
        else:
            return 'Death'
        
    df['phase'] = df['over'].apply(get_phase)
    logging.info("✓ Added boundary, dot ball and phase columns")
    
    
    
    logging.info(f"Deliveries transformation complete! Final shape: {df.shape}")
    return df


# this function is for saving the processed data

def save_processed_data(matches_df, deliveries_df):
    """
    Save cleaned dataframes to processed folder
    """
    os.makedirs('data/processed', exist_ok=True)
    
    matches_path    = 'data/processed/matches_clean.csv'
    deliveries_path = 'data/processed/deliveries_clean.csv'
    
    matches_df.save_processed_data    = matches_df.to_csv(matches_path, index=False)
    deliveries_df.save_processed_data = deliveries_df.to_csv(deliveries_path, index=False)
    
    logging.info(f"✓ Saved cleaned matches to {matches_path}")
    logging.info(f"✓ Saved cleaned deliveries to {deliveries_path}")
    
        
        
#main transform function where other functions will be called 

def transform_data():
    """
    Main transform function - runs full transformation
    """
    # First extract the data
    matches_df, deliveries_df = extract_data()
    
    if matches_df is None or deliveries_df is None:
        logging.error("Extraction failed - cannot transform")
        return None, None
    
    # Transform both dataframes
    matches_clean    = transform_matches(matches_df)
    deliveries_clean = transform_deliveries(deliveries_df)
    
    # Save to processed folder
    save_processed_data(matches_clean, deliveries_clean)
    
    return matches_clean, deliveries_clean


# Runs only when you run transform.py directly
if __name__ == "__main__":
    matches, deliveries = transform_data()
    
    if matches is not None:
        print("\n--- CLEANED MATCHES PREVIEW ---")
        print(f"Shape: {matches.shape}")
        print(matches[['id', 'season', 'date', 'team1', 
                        'team2', 'winner', 'win_type', 
                        'toss_match_winner']].head(5))
        
        print("\n--- WIN TYPE DISTRIBUTION ---")
        print(matches['win_type'].value_counts())
        
        print("\n--- TOSS IMPACT ---")
        toss_wins = matches['toss_match_winner'].value_counts()
        print(f"Toss winner won match: {toss_wins[True]} times")
        print(f"Toss winner lost match: {toss_wins[False]} times")
        
        print("\n--- CLEANED DELIVERIES PREVIEW ---")
        print(f"Shape: {deliveries.shape}")
        print(deliveries[['match_id', 'batter', 'bowler',
                           'batsman_runs', 'is_four', 
                           'is_six','is_Noball','phase']].head(5))
        
        print("\n--- PHASE DISTRIBUTION --- total deliveries")
        print(deliveries['phase'].value_counts())        
  