"""
Script to explore the euroleague-api package and confirm field names for E2025.
Run from the project root:  python scripts/explore_api.py

Confirmed valid gamecodes for E2025:
  Round 1: gamecodes 1-10
  Round 2: gamecodes 11-20
  (10 games per round in the regular season)

Note on the import warnings in VS Code:
  The package is installed in your user Python path. If VS Code shows
  "could not be resolved", go to:
  Ctrl+Shift+P → "Python: Select Interpreter" → pick Python 3.14
  (the one at C:\\Users\\loveN\\AppData\\Roaming\\Python\\Python314)
"""

import sys

SEASON = 2025
TEST_GAME_CODE = 1   # gamecode 1 = first game of Round 1, E2025
TEST_ROUND = 1

print(f"Testing euroleague-api for season {SEASON}\n")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: List gamecodes for the season — the right way to find them
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("SECTION 1: Season gamecodes")
print("=" * 60)
try:
    from euroleague_api.EuroLeagueData import EuroLeagueData

    base = EuroLeagueData()
    season_df = base.get_gamecodes_season(SEASON)
    played = season_df[season_df["played"]]
    print(f"Total games in E{SEASON}: {len(season_df)}, played: {len(played)}\n")
    print("First 20 played games:")
    print(played[["gameCode", "Round", "Phase", "homescore", "awayscore"]].head(20).to_string())

except Exception as e:
    print(f"ERROR in section 1: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Player boxscore for one game — confirm our field mapping
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"SECTION 2: Player boxscore — gamecode {TEST_GAME_CODE}")
print("=" * 60)
try:
    from euroleague_api.boxscore_data import BoxScoreData

    boxscore = BoxScoreData()
    df = boxscore.get_player_boxscore_stats_data(season=SEASON, gamecode=TEST_GAME_CODE)

    print(f"Rows (players): {len(df)}")
    print(f"All columns:\n  {list(df.columns)}\n")

    # Check that all fields we need for fantasy scoring are present
    needed = [
        "Points", "TotalRebounds", "Assistances", "Steals",
        "BlocksFavour", "Turnovers", "FoulsReceived", "FoulsCommited",
        "FieldGoalsMade2", "FieldGoalsAttempted2",
        "FieldGoalsMade3", "FieldGoalsAttempted3",
        "FreeThrowsMade", "FreeThrowsAttempted",
        "Minutes", "Player_ID", "Player",
    ]
    missing = [f for f in needed if f not in df.columns]
    if missing:
        print(f"WARNING: Missing expected fields: {missing}")
    else:
        print("All expected fantasy-scoring fields are present.\n")

    # Show top scorer's relevant stats
    # Filter out the "Total" summary row that the API appends at the end
    players_only = df[df["Player_ID"] != "Total"]
    if not players_only.empty:
        top = players_only.loc[players_only["Points"].idxmax()]
        print(f"Top scorer: {top.get('Player', '?')} ({top.get('Team', '?')})")
        for field in needed:
            print(f"  {field}: {top.get(field, 'N/A')}")

except Exception as e:
    print(f"ERROR in section 2: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Game metadata — for coach scoring (win/loss + margin)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"SECTION 3: Game metadata — gamecode {TEST_GAME_CODE}")
print("=" * 60)
try:
    from euroleague_api.game_metadata import GameMetadata  # type: ignore

    meta = GameMetadata()
    meta_df = meta.get_game_metadata(season=SEASON, gamecode=TEST_GAME_CODE)

    row = meta_df.iloc[0]
    print(f"Home team: {row['CodeTeamA']} ({row['TeamA']}) — Score: {row['ScoreA']}")
    print(f"Away team: {row['CodeTeamB']} ({row['TeamB']}) — Score: {row['ScoreB']}")
    print(f"CoachA: {row['CoachA']}")
    print(f"CoachB: {row['CoachB']}")

    margin_a = int(row["ScoreA"]) - int(row["ScoreB"])
    margin_b = -margin_a
    fp_a = (5 + margin_a) if margin_a > 0 else (-5 + margin_a)
    fp_b = (5 + margin_b) if margin_b > 0 else (-5 + margin_b)
    print(f"\nMargin for {row['CodeTeamA']}: {margin_a:+d}  => coach FP: {fp_a}")
    print(f"Margin for {row['CodeTeamB']}: {margin_b:+d}  => coach FP: {fp_b}")
    print("\nCoach scoring fields confirmed: CodeTeamA, CodeTeamB, ScoreA, ScoreB, CoachA, CoachB")

except Exception as e:
    print(f"ERROR in section 3: {e}")
