import os
import requests
import psycopg2
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

API_TOKEN = os.getenv('FOOTBALL_API_TOKEN')
DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "database": os.getenv('DB_NAME', 'ucl_db'),
    "user": os.getenv('DB_USER', 'postgres'),
    "password": os.getenv('DB_PASS'),
    "port": os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def setup_db():
    """Creates both tables required for the dashboard."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Standings Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ucl_standings (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL,
            position INTEGER,
            played INTEGER,
            points INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Matches Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ucl_matches (
            match_id INTEGER PRIMARY KEY,
            utc_date TIMESTAMP,
            status TEXT,
            matchday INTEGER,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            winner TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database tables verified/created.")

# --- STANDINGS LOGIC ---
def fetch_ucl_standings():
    url = "https://api.football-data.org/v4/competitions/CL/standings"
    headers = {'X-Auth-Token': API_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def sync_standings(data):
    if not data or 'standings' not in data: return
    standings_table = data['standings'][0]['table']
    conn = get_db_connection()
    cur = conn.cursor()
    
    for row in standings_table:
        cur.execute("""
            INSERT INTO ucl_standings (team_id, team_name, position, played, points, goals_for, goals_against, logo_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (team_id) DO UPDATE SET
                position = EXCLUDED.position, 
                played = EXCLUDED.played, 
                points = EXCLUDED.points,
                goals_for = EXCLUDED.goals_for,
                goals_against = EXCLUDED.goals_against,
                logo_url = EXCLUDED.logo_url,
                last_updated = CURRENT_TIMESTAMP;
        """, (
            row['team']['id'], 
            row['team']['name'], 
            row['position'], 
            row['playedGames'], 
            row['points'], 
            row['goalsFor'], 
            row['goalsAgainst'],
            row['team']['crest']  # <-- This is the API field for the logo
        ))
        
    conn.commit()
    cur.close()
    conn.close()
    print(f"Synced {len(standings_table)} teams (with logos) to ucl_standings.")

# --- MATCHES LOGIC ---
def fetch_ucl_matches():
    url = "https://api.football-data.org/v4/competitions/CL/matches"
    headers = {'X-Auth-Token': API_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def sync_matches(data):
    if not data or 'matches' not in data: return
    matches = data['matches']
    conn = get_db_connection()
    cur = conn.cursor()
    for m in matches:
        cur.execute("""
            INSERT INTO ucl_matches (match_id, utc_date, status, matchday, home_team_id, away_team_id, home_score, away_score, winner)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id) DO UPDATE SET
                status = EXCLUDED.status, home_score = EXCLUDED.home_score, 
                away_score = EXCLUDED.away_score, winner = EXCLUDED.winner,
                last_updated = CURRENT_TIMESTAMP;
        """, (m['id'], m['utcDate'], m['status'], m['matchday'], m['homeTeam']['id'], 
              m['awayTeam']['id'], m['score']['fullTime']['home'], 
              m['score']['fullTime']['away'], m['score']['winner']))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Synced {len(matches)} matches to ucl_matches.")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    try:
        setup_db()
        
        print("Starting Standings Sync...")
        standings_data = fetch_ucl_standings()
        sync_standings(standings_data)
        
        print("Starting Matches Sync...")
        matches_data = fetch_ucl_matches()
        sync_matches(matches_data)
        
        print("All data pipelines completed successfully!")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")