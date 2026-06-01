
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.transform import transform_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def create_db_engine():
    """
    Create SQLite database engine
    Database file will be created at data/ipl_database.db
    """
    os.makedirs('data', exist_ok=True)
    db_path = 'data/ipl_database.db'
    engine  = create_engine(f'sqlite:///{db_path}')
    logging.info(f"✓ Database engine created at {db_path}")
    return engine


#loading matches dataframe into database format 

def load_matches(matches_df, engine):
    logging.info("Loading matches into database...")
    
    try:
        # Load ALL columns directly - no renaming needed
        matches_df.to_sql(
            name='matches',
            con=engine,
            if_exists='replace',
            index=False
        )
        
        logging.info(f"✓ Loaded {len(matches_df)} rows into matches table")
        logging.info(f"✓ Columns loaded: {list(matches_df.columns)}")
        return True
        
    except Exception as e:
        logging.error(f"Error loading matches: {str(e)}")
        return False


def load_deliveries(deliveries_df, engine):
    logging.info("Loading deliveries into database...")
    
    try:
        # Load ALL columns
        deliveries_df.to_sql(
            name='deliveries',
            con=engine,
            if_exists='replace',
            index=False
        )
        
        logging.info(f"✓ Loaded {len(deliveries_df)} rows into deliveries table")
        logging.info(f"✓ Columns loaded: {list(deliveries_df.columns)}")
        return True
        
    except Exception as e:
        logging.error(f"Error loading deliveries: {str(e)}")
        return False
    
    

def load_team_stats(matches_df, engine):
    """
    Create and load a summary table for team statistics
    Pre-calculated to make Power BI queries faster
    """
    logging.info("Creating team stats summary table...")
    
    try:
        df = matches_df.copy()
        
        # Count wins per team
        wins = df[df['winner'] != 'No Result'].groupby('winner').size().reset_index()
        wins.columns = ['team', 'total_wins']
        
        # Count matches played as team1
        team1_matches = df.groupby('team1').size().reset_index()
        team1_matches.columns = ['team', 'matches_as_team1']
        
        # Count matches played as team2
        team2_matches = df.groupby('team2').size().reset_index()
        team2_matches.columns = ['team', 'matches_as_team2']
        
        # Merge everything together
        team_stats = wins.merge(team1_matches, on='team', how='left')
        team_stats = team_stats.merge(team2_matches, on='team', how='left')
        
        # Fill nulls and calculate total matches
        team_stats['matches_as_team1'] = team_stats['matches_as_team1'].fillna(0)
        team_stats['matches_as_team2'] = team_stats['matches_as_team2'].fillna(0)
        team_stats['total_matches']    = (
            team_stats['matches_as_team1'] + 
            team_stats['matches_as_team2']
        )
        
        # Calculate win percentage
        team_stats['win_percentage'] = (
            (team_stats['total_wins'] / team_stats['total_matches']) * 100
        ).round(2)
        
        # Sort by total wins
        team_stats = team_stats.sort_values('total_wins', ascending=False)
        
        # Load into SQL
        team_stats.to_sql(
            name='team_stats',
            con=engine,
            if_exists='replace',
            index=False
        )
        
        logging.info(f"✓ Loaded {len(team_stats)} teams into team_stats table")
        return True
        
    except Exception as e:
        logging.error(f"Error loading team stats: {str(e)}")
        return False
    
    
    


def verify_load(engine):
    """
    Verify data loaded correctly by running test SQL queries
    """
    logging.info("Verifying data load...")
    
    with engine.connect() as conn:
        
        # Check row counts in all 3 tables
        matches_count    = conn.execute(text("SELECT COUNT(*) FROM matches")).scalar()
        deliveries_count = conn.execute(text("SELECT COUNT(*) FROM deliveries")).scalar()
        teams_count      = conn.execute(text("SELECT COUNT(*) FROM team_stats")).scalar()
        
        logging.info(f"✓ matches table    : {matches_count} rows")
        logging.info(f"✓ deliveries table : {deliveries_count} rows")
        logging.info(f"✓ team_stats table : {teams_count} rows")
        
        # Test query 1 - top 5 teams by wins
        result = conn.execute(text("""
            SELECT team, total_wins, win_percentage 
            FROM team_stats 
            ORDER BY total_wins DESC 
            LIMIT 5
        """))
        
        print("\n--- TOP 5 TEAMS BY WINS ---")
        print(f"{'Team':<35} {'Wins':<10} {'Win %'}")
        print("-" * 55)
        for row in result:
            print(f"{row[0]:<35} {row[1]:<10} {row[2]}%")
        
        # Test query 2 - toss impact
        result2 = conn.execute(text("""
            SELECT toss_match_winner, COUNT(*) as count
            FROM matches
            GROUP BY toss_match_winner
        """))
        
        print("\n--- TOSS IMPACT ---")
        for row in result2:
            label = "Toss winner WON match" if row[0] == 1 else "Toss winner LOST match"
            print(f"{label} : {row[1]} times")
        
        # Test query 3 - most player of match awards
        result3 = conn.execute(text("""
            SELECT player_of_match, COUNT(*) as awards
            FROM matches
            WHERE player_of_match != 'Unknown'
            GROUP BY player_of_match
            ORDER BY awards DESC
            LIMIT 5
        """))
        
        print("\n--- TOP 5 PLAYER OF MATCH WINNERS ---")
        for row in result3:
            print(f"{row[0]:<25} : {row[1]} awards")
            
            



## maine function yaha se sara cleaned data load hoke database main jayega

def load_data():
    """
    Main load function - runs full pipeline
    Extract → Transform → Load → Verify
    """
    # Get transformed clean data
    matches_df, deliveries_df = transform_data()
    
    if matches_df is None or deliveries_df is None:
        logging.error("Transform failed - cannot load")
        return False
    
    # Create database engine
    engine = create_db_engine()
    
    # Load all 3 tables
    load_matches(matches_df, engine)
    load_deliveries(deliveries_df, engine)
    load_team_stats(matches_df, engine)
    
    # Verify everything loaded correctly
    verify_load(engine)
    
    logging.info("🎉 Full pipeline complete! Database ready.")
    return True


if __name__ == "__main__":
    load_data()

