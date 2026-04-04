import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
API_TOKEN = os.getenv('FOOTBALL_API_TOKEN')

def fetch_ucl_data():
    url = "https://api.football-data.org/v4/competitions/CL/standings"
    headers = {'X-Auth-Token': API_TOKEN}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Connected to: {data['competition']['name']}")
        
        # Print the first group standings as a test
        standings = data['standings'][0]
        print(f"--- {standings['group']} ---")
        for team in standings['table']:
            print(f"{team['position']}. {team['team']['name']} ({team['points']} pts)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_ucl_data()