import pandas as pd 
import os
import logging


# Setup logging - this prints status messages in terminal
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

"""
Extract raw csv files create a function for that 
"""

def extract_data():
    matches_path = 'data/raw/matches.csv'
    deliveries_path = 'data/raw/deliveries.csv'
    
    
    # Check if files exist before reading
    if not os.path.exists(matches_path):
        logging.error(f"matches.csv not found at {matches_path}")
        return None, None
        
    if not os.path.exists(deliveries_path):
        logging.error(f"deliveries.csv not found at {deliveries_path}")
        return None, None
    
    try:
        logging.info("Reading matches.csv")
        matches_df = pd.read_csv(matches_path)
        logging.info(f"Extracted {len(matches_df)} match records")
        
        
        #deliveries file read karte hai
        logging.info("Reading deliveries.csv")
        deliveries_df=pd.read_csv(deliveries_path)
        logging.info(f"Extracted {len(deliveries_df)} delivery records")
        
           
# quick check if expected columns exist or not 

 # Quick validation - check expected columns exist
        expected_match_cols = ['id', 'season', 'city', 'date', 'winner']
        expected_delivery_cols = ['match_id', 'inning', 'batter', 'bowler', 'total_runs']
        
        for col in expected_match_cols:
            if col not in matches_df.columns:
                logging.error(f"Missing expected column in matches: {col}")
                return None, None
                
        for col in expected_delivery_cols:
            if col not in deliveries_df.columns:
                logging.error(f"Missing expected column in deliveries: {col}")
                return None, None
            
            
        logging.info("Extraction complete! Both files validated successfully ✓")
        return matches_df, deliveries_df    

    except Exception as e:
        logging.error(f"Error during extraction: {str(e)}")
        return None, None
    
    
    
# This runs only when you run extract.py directly
if __name__ == "__main__":
    matches, deliveries = extract_data()
    
    if matches is not None:
        print("\n--- MATCHES PREVIEW ---")
        print(f"Shape: {matches.shape}")
        print(matches.head(3))
        
        print("\n--- DELIVERIES PREVIEW ---")
        print(f"Shape: {deliveries.shape}")
        print(deliveries.head(3))
        
        print("\n--- NULL VALUES IN MATCHES ---")
        print(matches.isnull().sum())
        
        print("\n--- NULL VALUES IN DELIVERIES ---")
        print(deliveries.isnull().sum())