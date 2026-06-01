import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import pandas as pd
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Analysis.insights import (
    get_data,
    q1_team_win_percentage,
    q2_toss_impact,
    q3_bat_first_vs_chase,
    q4_top_batsmen,
    q5_top_bowlers,
    q6_most_pom_awards,
    q9_phase_boundaries,
    q10_team_powerplay_performance
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Chart style setup
sns.set_theme(style='darkgrid')
CHART_DIR = 'charts'
os.makedirs(CHART_DIR, exist_ok=True)



def chart_q1(matches_df):
    """Bar chart — Team win percentages"""
    logging.info("📊 Creating Q1 chart...")
    
    data = q1_team_win_percentage(matches_df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(data.index, data['win_percentage'], color=sns.color_palette('viridis', len(data)))
    
    ax.set_xlabel('Win Percentage (%)')
    ax.set_title('🏆 Team Win Percentage — All Time', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add value labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{width}%', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q1_team_win_percentage.png', dpi=150)
    plt.close()
    logging.info("✓ Q1 chart saved")




def chart_q2(matches_df):
    """Pie chart + bar chart — Toss impact analysis"""
    logging.info("📊 Creating Q2 chart...")
    
    summary, season_trend = q2_toss_impact(matches_df)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left — Pie chart overall toss impact
    colors = ['#2ecc71', '#e74c3c']
    ax1.pie(summary['count'], labels=summary['outcome'], autopct='%1.1f%%',
            colors=colors, startangle=90, textprops={'fontsize': 10})
    ax1.set_title('🎲 Overall Toss Impact', fontsize=13, fontweight='bold')
    
    # Right — Season wise trend line
    ax2.plot(season_trend['season'], season_trend['win_percentage'], 
             marker='o', color='#3498db', linewidth=2, markersize=6)
    ax2.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% line')
    ax2.set_xlabel('Season')
    ax2.set_ylabel('Toss Winner Win %')
    ax2.set_title('📈 Toss Impact Over Seasons', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q2_toss_impact.png', dpi=150)
    plt.close()
    logging.info("✓ Q2 chart saved")

def chart_q3(matches_df):
    """Bar chart — Bat first vs Chase"""
    logging.info("📊 Creating Q3 chart...")
    
    summary, season_trend = q3_bat_first_vs_chase(matches_df)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left — overall comparison
    colors = ['#e67e22', '#27ae60']
    ax1.bar(summary['strategy'], summary['count'], color=colors, width=0.5)
    for i, row in summary.iterrows():
        ax1.text(i, row['count'] + 3, f"{row['percentage']}%", 
                 ha='center', fontweight='bold')
    ax1.set_title('🏏 Bat First vs Chase — Overall', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Number of Wins')
    
    # Right — chase win % trend over seasons
    ax2.bar(season_trend['season'], season_trend['chase_win_pct'], 
            color='#27ae60', alpha=0.8)
    ax2.axhline(y=50, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Season')
    ax2.set_ylabel('Chase Win %')
    ax2.set_title('📈 Chase Win % Over Seasons', fontsize=13, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q3_bat_vs_chase.png', dpi=150)
    plt.close()
    logging.info("✓ Q3 chart saved")


def chart_q4(deliveries_df, matches_df):
    """Horizontal bar chart — Top 10 batsmen"""
    logging.info("📊 Creating Q4 chart...")
    
    data = q4_top_batsmen(deliveries_df, matches_df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette('magma', len(data))
    bars = ax.barh(data['batter'], data['total_runs'], color=colors)
    
    ax.set_xlabel('Total Runs')
    ax.set_title('⭐ Top 10 Batsmen — All Time Runs', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add runs + strike rate labels
    for i, (bar, sr) in enumerate(zip(bars, data['strike_rate'])):
        width = bar.get_width()
        ax.text(width + 50, bar.get_y() + bar.get_height()/2,
                f'{int(width)} runs (SR: {sr})', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q4_top_batsmen.png', dpi=150)
    plt.close()
    logging.info("✓ Q4 chart saved")


def chart_q5(deliveries_df):
    """Horizontal bar chart — Top 10 bowlers"""
    logging.info("📊 Creating Q5 chart...")
    
    data = q5_top_bowlers(deliveries_df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette('cool', len(data))
    bars = ax.barh(data['bowler'], data['total_wickets'], color=colors)
    
    ax.set_xlabel('Total Wickets')
    ax.set_title('🎳 Top 10 Bowlers — All Time Wickets', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add wickets + economy labels
    for i, (bar, eco) in enumerate(zip(bars, data['economy'])):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{int(width)} wkts (Eco: {eco})', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q5_top_bowlers.png', dpi=150)
    plt.close()
    logging.info("✓ Q5 chart saved")


def chart_q6(matches_df):
    """Bar chart — Most Player of Match awards"""
    logging.info("📊 Creating Q6 chart...")
    
    data = q6_most_pom_awards(matches_df)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette('rocket', len(data))
    bars = ax.barh(data['player'], data['pom_awards'], color=colors)
    
    ax.set_xlabel('POM Awards')
    ax.set_title('🏅 Most Player of Match Awards', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                f'{int(width)}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q6_pom_awards.png', dpi=150)
    plt.close()
    logging.info("✓ Q6 chart saved")


def chart_q9(deliveries_df):
    """Grouped bar chart — Boundaries by phase"""
    logging.info("📊 Creating Q9 chart...")
    
    data = q9_phase_boundaries(deliveries_df)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left — Fours vs Sixes by phase
    x = range(len(data))
    width = 0.35
    ax1.bar([i - width/2 for i in x], data['fours'], width, label='Fours', color='#3498db')
    ax1.bar([i + width/2 for i in x], data['sixes'], width, label='Sixes', color='#e74c3c')
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(data['phase'])
    ax1.set_ylabel('Count')
    ax1.set_title('💥 Fours vs Sixes by Phase', fontsize=13, fontweight='bold')
    ax1.legend()
    
    # Right — Run rate by phase
    ax2.bar(data['phase'], data['run_rate'], color=['#2ecc71', '#f39c12', '#e74c3c'])
    for i, v in enumerate(data['run_rate']):
        ax2.text(i, v + 0.1, f'{v}', ha='center', fontweight='bold')
    ax2.set_ylabel('Run Rate (per over)')
    ax2.set_title('📈 Run Rate by Phase', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q9_phase_boundaries.png', dpi=150)
    plt.close()
    logging.info("✓ Q9 chart saved")


def chart_q10(deliveries_df, matches_df):
    """Bar chart — Team powerplay performance"""
    logging.info("📊 Creating Q10 chart...")
    
    data = q10_team_powerplay_performance(deliveries_df, matches_df)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Top — Avg powerplay runs per team
    ax1.barh(data['team'], data['avg_pp_runs'], color=sns.color_palette('viridis', len(data)))
    ax1.set_xlabel('Avg Powerplay Runs')
    ax1.set_title('⚡ Team Avg Powerplay Runs', fontsize=13, fontweight='bold')
    ax1.invert_yaxis()
    
    # Bottom — Avg powerplay wickets lost
    ax2.barh(data['team'], data['avg_pp_wickets'], color=sns.color_palette('rocket', len(data)))
    ax2.set_xlabel('Avg Powerplay Wickets Lost')
    ax2.set_title('📉 Team Avg Powerplay Wickets Lost', fontsize=13, fontweight='bold')
    ax2.invert_yaxis()

    plt.tight_layout()
    plt.savefig(f'{CHART_DIR}/q10_team_powerplay.png', dpi=150)
    plt.close()
    logging.info("✓ Q10 chart saved")

def main():
    logging.info("Starting chart generation...")
    matches_df, deliveries_df = get_data()
    
    if matches_df is None or deliveries_df is None:
        logging.error("Could not load data. Ensure ETL is complete.")
        return

    chart_q1(matches_df)
    chart_q2(matches_df)
    chart_q3(matches_df)
    chart_q4(deliveries_df, matches_df)
    chart_q5(deliveries_df)
    chart_q6(matches_df)
    chart_q9(deliveries_df)
    chart_q10(deliveries_df, matches_df)
    
    logging.info(f"All charts generated in '{CHART_DIR}/' successfully!")

if __name__ == "__main__":
    main()




