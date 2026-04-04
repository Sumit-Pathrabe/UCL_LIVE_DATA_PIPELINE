import os
import requests
import psycopg2
from psycopg2.extras import execute_values
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
    """Returns a connection to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

def setup_db():
    """Creates the UCL table if it doesn't exist."""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS ucl_standings (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL,
            position INTEGER,
            played INTEGER,
            points INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    )
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
        print("Database table ready.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"DB Setup Error: {error}")
    finally:
        if conn is not None:
            conn.close()

def fetch_ucl_data():
    """Fetches the latest UCL League Phase standings from the API."""
    url = "https://api.football-data.org/v4/competitions/CL/standings"
    headers = {'X-Auth-Token': API_TOKEN}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Fetch Error: {e}")
        return None

def sync_to_postgres(data):
    """Parses API data and performs an UPSERT into PostgreSQL."""
    if not data or 'standings' not in data:
        print("No valid data to sync.")
        return

    # In the new UCL format, standings[0] contains the full league table
    standings_table = data['standings'][0]['table']
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        for row in standings_table:
            # UPSERT Logic: Insert if new, Update points/position if team_id exists
            cur.execute("""
                INSERT INTO ucl_standings (team_id, team_name, position, played, points, goals_for, goals_against)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (team_id) DO UPDATE SET
                    position = EXCLUDED.position,
                    played = EXCLUDED.played,
                    points = EXCLUDED.points,
                    goals_for = EXCLUDED.goals_for,
                    goals_against = EXCLUDED.goals_against,
                    last_updated = CURRENT_TIMESTAMP;
            """, (
                row['team']['id'],
                row['team']['name'],
                row['position'],
                row['playedGames'],
                row['points'],
                row['goalsFor'],
                row['goalsAgainst']
            ))

        conn.commit()
        cur.close()
        print(f"Successfully synced {len(standings_table)} teams to Postgres.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Sync Error: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    # Ensure database is ready
    setup_db()
    
    # Run the pipeline
    print("Fetching UCL data...")
    raw_data = fetch_ucl_data()
    
    if raw_data:
        sync_to_postgres(raw_data)