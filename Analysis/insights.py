import pandas as pd
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_data():
    """
    Load cleaned data from SQLite database
    Returns matches and deliveries as DataFrames
    """
    db_path = 'data/ipl_database.db'
    
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}. Run load.py first!")
        return None, None
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    logging.info("Loading data from database...")
    matches_df    = pd.read_sql('SELECT * FROM matches', engine)
    deliveries_df = pd.read_sql('SELECT * FROM deliveries', engine)
    
    logging.info(f"✓ Loaded {len(matches_df)} matches and {len(deliveries_df)} deliveries")
    return matches_df, deliveries_df



    #--------------------------------
    # Team performence
    #--------------------------------


def q1_team_win_percentage(matches_df):
    """
    Q1. Which team has highest win percentage all time?
    Prediction use: Team most likely to win based on historical consistency
    """
    logging.info("Q1: Calculating team win percentages...")
    
    # Count total matches per team (played as team1 + team2)
    team1 = matches_df.groupby('team1').size()
    team2 = matches_df.groupby('team2').size()
    total_matches = (team1.add(team2, fill_value=0)).astype(int)
    
    # Count wins per team
    wins = matches_df[matches_df['winner'] != 'No Result'] \
               .groupby('winner').size()
    
    # Build summary dataframe
    summary = pd.DataFrame({
        'total_matches': total_matches,
        'total_wins':    wins
    }).fillna(0).astype(int)
    
    summary['win_percentage'] = (
        (summary['total_wins'] / summary['total_matches']) * 100
    ).round(2)
    
    summary = summary.sort_values('win_percentage', ascending=False)
    
    logging.info(f"✓ Q1 complete — Top team: {summary.index[0]} "
                 f"with {summary['win_percentage'].iloc[0]}% win rate")
    
    return summary




def q2_toss_impact(matches_df):
    """
    Q2. Does winning toss actually help win the match?
    Prediction use: Should toss be a factor in match prediction model?
    """
    logging.info("Q2: Analyzing toss impact on match results...")
    
    # Filter out no result matches
    df = matches_df[matches_df['winner'] != 'No Result'].copy()
    
    # Check if toss winner won the match
    df['toss_winner_won'] = df['toss_winner'] == df['winner']
    
    toss_wins = df['toss_winner_won'].sum()
    toss_losses = len(df) - toss_wins
    total = len(df)
    
    # Build summary
    summary = pd.DataFrame({
        'outcome':    ['Toss winner WON match', 'Toss winner LOST match'],
        'count':      [toss_wins, toss_losses],
        'percentage': [
            round((toss_wins / total) * 100, 2),
            round((toss_losses / total) * 100, 2)
        ]
    })
    
    # Season wise toss impact trend
    season_toss = df.groupby('season')['toss_winner_won'].agg(
        toss_wins='sum',
        total_matches='count'
    ).reset_index()
    
    season_toss['win_percentage'] = (
        (season_toss['toss_wins'] / season_toss['total_matches']) * 100
    ).round(2)
    
    logging.info(f"✓ Q2 complete — Toss winner won {toss_wins}/{total} "
                 f"({round((toss_wins/total)*100, 1)}%) matches")
    
    return summary, season_toss






def q3_bat_first_vs_chase(matches_df):
    """
    Q3. Batting first vs chasing — which strategy wins more?
    Prediction use: Key input for match outcome prediction
    """
    logging.info("Q3: Analyzing bat first vs chase win rates...")
    
    # Filter out no result matches
    df = matches_df[matches_df['winner'] != 'No Result'].copy()
    
    # If winner == team batting first (toss_decision tells us)
    # bat first: toss winner chose bat AND won, OR toss loser fielded AND lost
    df['bat_first_team'] = df.apply(
        lambda row: row['team1'] if row['toss_decision'] == 'bat' and row['toss_winner'] == row['team1']
                     else row['team2'] if row['toss_decision'] == 'bat' and row['toss_winner'] == row['team2']
                     else row['team2'] if row['toss_decision'] == 'field' and row['toss_winner'] == row['team1']
                     else row['team1'], axis=1
    )
    
    df['bat_first_won'] = df['bat_first_team'] == df['winner']
    
    bat_first_wins = df['bat_first_won'].sum()
    chase_wins     = len(df) - bat_first_wins
    total          = len(df)
    
    # Overall summary
    summary = pd.DataFrame({
        'strategy':   ['Bat First Won', 'Chasing Won'],
        'count':      [bat_first_wins, chase_wins],
        'percentage': [
            round((bat_first_wins / total) * 100, 2),
            round((chase_wins / total) * 100, 2)
        ]
    })
    
    # Season wise trend — is chasing becoming more dominant?
    season_trend = df.groupby('season')['bat_first_won'].agg(
        bat_first_wins='sum',
        total_matches='count'
    ).reset_index()
    
    season_trend['chase_wins']        = season_trend['total_matches'] - season_trend['bat_first_wins']
    season_trend['chase_win_pct']     = (
        (season_trend['chase_wins'] / season_trend['total_matches']) * 100
    ).round(2)
    
    logging.info(f"✓ Q3 complete — Bat first: {bat_first_wins} wins | "
                 f"Chase: {chase_wins} wins out of {total} matches")
    
    return summary, season_trend





# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏏 PLAYER ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def q4_top_batsmen(deliveries_df, matches_df):
    """
    Q4. Top 10 batsmen by total runs — who is the GOAT?
    Prediction use: Player form and consistency metric
    """
    logging.info("Q4: Finding top 10 batsmen by total runs...")
    
    # Total runs per batter
    batter_runs = deliveries_df.groupby('batter')['batsman_runs'].agg(
        total_runs='sum',
        balls_faced='count',
        fours=lambda x: (x == 4).sum(),
        sixes=lambda x: (x == 6).sum()
    ).reset_index()
    
    # How many matches each batter played
    matches_played = deliveries_df.groupby('batter')['match_id'] \
                         .nunique().reset_index()
    matches_played.columns = ['batter', 'matches_played']
    
    # Merge matches played with runs
    batter_runs = batter_runs.merge(matches_played, on='batter')
    
    # Calculate strike rate and average
    batter_runs['strike_rate'] = (
        (batter_runs['total_runs'] / batter_runs['balls_faced']) * 100
    ).round(2)
    
    batter_runs['average'] = (
        batter_runs['total_runs'] / batter_runs['matches_played']
    ).round(2)
    
    # Sort and get top 10
    top_10 = batter_runs.sort_values('total_runs', ascending=False).head(10)
    
    logging.info(f"✓ Q4 complete — Top scorer: {top_10.iloc[0]['batter']} "
                 f"with {top_10.iloc[0]['total_runs']} runs")
    
    return top_10





def q5_top_bowlers(deliveries_df):
    """
    Q5. Top 10 bowlers by total wickets
    Prediction use: Bowling impact on team win probability
    """
    logging.info("Q5: Finding top 10 bowlers by total wickets...")
    
    # Only count real dismissals (not run outs — bowler doesn't get credit)
    valid_dismissals = deliveries_df[
        (deliveries_df['dismissal_kind'] != 'not_out') &
        (deliveries_df['dismissal_kind'] != 'run out') &
        (deliveries_df['dismissal_kind'] != 'retired hurt') &
        (deliveries_df['dismissal_kind'] != 'obstructing the field')
    ]
    
    # Wickets per bowler
    wickets = valid_dismissals.groupby('bowler').size().reset_index()
    wickets.columns = ['bowler', 'total_wickets']
    
    # Balls bowled and runs conceded per bowler
    bowler_stats = deliveries_df.groupby('bowler').agg(
        balls_bowled=('bowler', 'count'),
        runs_conceded=('total_runs', 'sum'),
        matches_played=('match_id', 'nunique')
    ).reset_index()
    
    # Merge wickets with bowling stats
    bowler_stats = bowler_stats.merge(wickets, on='bowler', how='left')
    bowler_stats['total_wickets'] = bowler_stats['total_wickets'].fillna(0).astype(int)
    
    # Calculate economy rate (runs per over)
    bowler_stats['economy'] = (
        (bowler_stats['runs_conceded'] / (bowler_stats['balls_bowled'] / 6))
    ).round(2)
    
    # Calculate bowling average (runs per wicket)
    bowler_stats['bowling_avg'] = bowler_stats.apply(
        lambda row: round(row['runs_conceded'] / row['total_wickets'], 2) 
                    if row['total_wickets'] > 0 else 0, axis=1
    )
    
    # Sort and get top 10
    top_10 = bowler_stats.sort_values('total_wickets', ascending=False).head(10)
    
    logging.info(f"✓ Q5 complete — Top wicket taker: {top_10.iloc[0]['bowler']} "
                 f"with {top_10.iloc[0]['total_wickets']} wickets")
    
    return top_10





def q6_most_pom_awards(matches_df):
    """
    Q6. Which players win Player of Match most?
    Prediction use: Most impactful players — key feature for prediction
    """
    logging.info("Q6: Finding most Player of Match award winners...")
    
    # Filter out Unknown (we filled nulls with 'Unknown' in transform)
    df = matches_df[matches_df['player_of_match'] != 'Unknown']
    
    # Count awards per player
    pom_counts = df.groupby('player_of_match').size().reset_index()
    pom_counts.columns = ['player', 'pom_awards']
    
    # How many matches each player was part of (as team1 or team2 player)
    # We can approximate by counting seasons they appeared in
    seasons_active = df.groupby('player_of_match')['season'].nunique().reset_index()
    seasons_active.columns = ['player', 'seasons_active']
    
    # Merge
    pom_counts = pom_counts.merge(seasons_active, on='player')
    
    # Awards per season — shows consistency
    pom_counts['awards_per_season'] = (
        pom_counts['pom_awards'] / pom_counts['seasons_active']
    ).round(2)
    
    # Sort by total awards
    pom_counts = pom_counts.sort_values('pom_awards', ascending=False)
    
    top_10 = pom_counts.head(10)
    
    logging.info(f"✓ Q6 complete — Most awards: {top_10.iloc[0]['player']} "
                 f"with {top_10.iloc[0]['pom_awards']} POM awards")
    
    return top_10





# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ GAME STRATEGY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def q9_phase_boundaries(deliveries_df):
    """
    Q9. Which phase has most boundaries — powerplay, middle or death?
    Prediction use: Phase wise scoring pattern for strategy prediction
    """
    logging.info("Q9: Analyzing boundaries by game phase...")
    
    # Phase wise boundary counts
    phase_stats = deliveries_df.groupby('phase').agg(
        total_balls=('phase', 'count'),
        total_runs=('total_runs', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dot_balls=('is_dot_ball', 'sum')
    ).reset_index()
    
    # Total boundaries
    phase_stats['total_boundaries'] = phase_stats['fours'] + phase_stats['sixes']
    
    # Boundary percentage — what % of balls are boundaries
    phase_stats['boundary_pct'] = (
        (phase_stats['total_boundaries'] / phase_stats['total_balls']) * 100
    ).round(2)
    
    # Dot ball percentage
    phase_stats['dot_ball_pct'] = (
        (phase_stats['dot_balls'] / phase_stats['total_balls']) * 100
    ).round(2)
    
    # Average runs per ball in each phase
    phase_stats['run_rate'] = (
        (phase_stats['total_runs'] / phase_stats['total_balls']) * 6
    ).round(2)
    
    # Order phases logically
    phase_order = {'Powerplay': 0, 'Middle': 1, 'Death': 2}
    phase_stats['order'] = phase_stats['phase'].map(phase_order)
    phase_stats = phase_stats.sort_values('order').drop('order', axis=1)
    
    logging.info(f"✓ Q9 complete — Most boundaries in: "
                 f"{phase_stats.loc[phase_stats['total_boundaries'].idxmax(), 'phase']} phase")
    
    return phase_stats






def q10_team_powerplay_performance(deliveries_df, matches_df):
    """
    Q10. Which team has best powerplay performance — runs scored and wickets taken?
    Prediction use: Powerplay performance strongly correlates with match result
    """
    logging.info("Q10: Analyzing team powerplay performance...")
    
    # Filter only powerplay overs
    pp = deliveries_df[deliveries_df['phase'] == 'Powerplay'].copy()
    
    # ── BATTING in powerplay ──
    pp_batting = pp.groupby(['match_id', 'batting_team']).agg(
        pp_runs=('total_runs', 'sum'),
        pp_balls=('batting_team', 'count'),
        pp_fours=('is_four', 'sum'),
        pp_sixes=('is_six', 'sum')
    ).reset_index()
    
    # Average powerplay score per team
    batting_summary = pp_batting.groupby('batting_team').agg(
        matches=('match_id', 'nunique'),
        avg_pp_runs=('pp_runs', 'mean'),
        avg_pp_fours=('pp_fours', 'mean'),
        avg_pp_sixes=('pp_sixes', 'mean')
    ).reset_index().round(2)
    
    batting_summary.columns = ['team', 'matches', 'avg_pp_runs', 
                               'avg_pp_fours', 'avg_pp_sixes']
    
    # ── BOWLING in powerplay (wickets taken) ──
    pp_wickets = pp[
        (pp['dismissal_kind'] != 'not_out') &
        (pp['dismissal_kind'] != 'run out')
    ]
    
    bowling_wickets = pp_wickets.groupby(['match_id', 'bowling_team']).size() \
                          .reset_index()
    bowling_wickets.columns = ['match_id', 'team', 'pp_wickets']
    
    bowling_summary = bowling_wickets.groupby('team').agg(
        avg_pp_wickets=('pp_wickets', 'mean')
    ).reset_index().round(2)
    
    # Merge batting and bowling powerplay stats
    pp_summary = batting_summary.merge(bowling_summary, on='team', how='left')
    pp_summary['avg_pp_wickets'] = pp_summary['avg_pp_wickets'].fillna(0)
    
    # Sort by avg powerplay runs
    pp_summary = pp_summary.sort_values('avg_pp_runs', ascending=False)
    
    logging.info(f"✓ Q10 complete — Best PP batting: {pp_summary.iloc[0]['team']} "
                 f"with avg {pp_summary.iloc[0]['avg_pp_runs']} runs")
    
    return pp_summary




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 RUN ALL INSIGHTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    matches, deliveries = get_data()
    
    if matches is None:
        print("❌ Failed to load data. Run load.py first!")
    else:
        print("\n" + "="*60)
        print("🏆 Q1: TEAM WIN PERCENTAGE")
        print("="*60)
        print(q1_team_win_percentage(matches).to_string())
        
        print("\n" + "="*60)
        print("🎲 Q2: TOSS IMPACT")
        print("="*60)
        summary, season = q2_toss_impact(matches)
        print(summary.to_string(index=False))
        
        print("\n" + "="*60)
        print("🏏 Q3: BAT FIRST vs CHASE")
        print("="*60)
        summary, trend = q3_bat_first_vs_chase(matches)
        print(summary.to_string(index=False))
        
        print("\n" + "="*60)
        print("⭐ Q4: TOP 10 BATSMEN")
        print("="*60)
        print(q4_top_batsmen(deliveries, matches).to_string(index=False))
        
        print("\n" + "="*60)
        print("🎳 Q5: TOP 10 BOWLERS")
        print("="*60)
        print(q5_top_bowlers(deliveries).to_string(index=False))
        
        print("\n" + "="*60)
        print("🏅 Q6: MOST PLAYER OF MATCH AWARDS")
        print("="*60)
        print(q6_most_pom_awards(matches).to_string(index=False))
        
        print("\n" + "="*60)
        print("💥 Q9: BOUNDARIES BY PHASE")
        print("="*60)
        print(q9_phase_boundaries(deliveries).to_string(index=False))
        
        print("\n" + "="*60)
        print("⚡ Q10: TEAM POWERPLAY PERFORMANCE")
        print("="*60)
        print(q10_team_powerplay_performance(deliveries, matches).to_string(index=False))
        
        logging.info("🎉 All insights generated successfully!")










          

