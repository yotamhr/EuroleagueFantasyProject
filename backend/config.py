from pathlib import Path

# Euroleague season (2025-26 season uses code 2025)
SEASON_CODE = 2025

# Paths to data files
DATA_DIR = Path(__file__).parent.parent / "data"
PLAYERS_FILE = DATA_DIR / "players.json"
COACHES_FILE = DATA_DIR / "coaches.json"
STATS_DIR = DATA_DIR / "stats"
SQUADS_DIR = DATA_DIR / "squads"
