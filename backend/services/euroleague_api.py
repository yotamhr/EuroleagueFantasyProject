"""
Wrapper around the euroleague-api PyPI package.
Fetches player stats and game results for a given round,
then returns data in the format the app expects.

Confirmed API field mapping (from explore_api.py):
  Points                 -> points
  TotalRebounds          -> rebounds
  Assistances            -> assists
  Steals                 -> steals
  BlocksFavour           -> blocks
  Turnovers              -> turnovers
  FoulsReceived          -> fouls_drawn
  FoulsCommited          -> fouls_committed   (API has a typo: one 't')
  FieldGoalsMade2        -> fg2_made
  FieldGoalsAttempted2   -> fg2_attempted
  FieldGoalsMade3        -> fg3_made
  FieldGoalsAttempted3   -> fg3_attempted
  FreeThrowsMade         -> ft_made
  FreeThrowsAttempted    -> ft_attempted
  Minutes                -> minutes_played
  Player_ID              -> player_euroleague_id
  Player                 -> player_name
  Team                   -> team_code

Coach scoring (from GameMetadata):
  CodeTeamA / CodeTeamB  -> team codes
  ScoreA / ScoreB        -> final scores
  margin = ScoreA - ScoreB (positive for team A, negative for team B)
"""

import json
import logging

from config import SEASON_CODE, PLAYERS_FILE
from services.fantasy_scorer import compute_fantasy_points, compute_coach_fantasy_points

logger = logging.getLogger(__name__)

PLAYER_FIELD_MAP = {
    "Points": "points",
    "TotalRebounds": "rebounds",
    "Assistances": "assists",
    "Steals": "steals",
    "BlocksFavour": "blocks",
    "Turnovers": "turnovers",
    "FoulsReceived": "fouls_drawn",
    "FoulsCommited": "fouls_committed",
    "FieldGoalsMade2": "fg2_made",
    "FieldGoalsAttempted2": "fg2_attempted",
    "FieldGoalsMade3": "fg3_made",
    "FieldGoalsAttempted3": "fg3_attempted",
    "FreeThrowsMade": "ft_made",
    "FreeThrowsAttempted": "ft_attempted",
    "Minutes": "minutes_played",
    "Player_ID": "player_euroleague_id",
    "Player": "player_name",
    "Team": "team_code",
}

INT_FIELDS = {
    "points", "rebounds", "assists", "steals", "blocks", "turnovers",
    "fouls_drawn", "fouls_committed", "fg2_made", "fg2_attempted",
    "fg3_made", "fg3_attempted", "ft_made", "ft_attempted",
}


def _load_players() -> list:
    if not PLAYERS_FILE.exists():
        return []
    with open(PLAYERS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_players(players: list) -> None:
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)


def _update_player_ids(players: list, api_players: list) -> None:
    """
    Auto-match players in our JSON file to the Euroleague API by name.
    Updates euroleague_player_id in-place and persists to disk.
    """
    api_by_name = {
        p["player_name"].lower().strip(): p["player_euroleague_id"]
        for p in api_players
        if p.get("player_euroleague_id") and p.get("player_name")
    }

    changed = False
    unmatched = []
    for player in players:
        if player.get("euroleague_player_id"):
            continue
        normalized = player["name"].lower().strip()
        if normalized in api_by_name:
            player["euroleague_player_id"] = api_by_name[normalized]
            changed = True
            logger.info(f"Matched player '{player['name']}' -> {player['euroleague_player_id']}")
        else:
            unmatched.append(player["name"])

    if changed:
        _save_players(players)
    if unmatched:
        logger.warning(f"Could not auto-match {len(unmatched)} player(s): {unmatched}")


def _map_player_row(row: dict) -> dict:
    """Map one row of raw API data to our internal player stats format."""
    mapped = {}
    for api_field, our_field in PLAYER_FIELD_MAP.items():
        val = row.get(api_field)
        if val is None:
            mapped[our_field] = 0 if our_field in INT_FIELDS else ""
        elif our_field in INT_FIELDS:
            try:
                mapped[our_field] = int(val)
            except (ValueError, TypeError):
                mapped[our_field] = 0
        else:
            mapped[our_field] = str(val) if val is not None else ""
    return mapped


def fetch_round_stats(round_number: int) -> dict:
    """
    Fetch all player and coach stats for a given round.
    Returns a dict ready to be saved as round_N.json.

    Strategy:
    1. Use get_gamecodes_season() to get the full list of gamecodes and which
       round each belongs to. This avoids blind iteration.
    2. Filter to the gamecodes for our target round.
    3. Fetch player boxscore for each game.
    4. Fetch game metadata (scores) for coach scoring.
    """
    from euroleague_api.boxscore_data import BoxScoreData  # type: ignore
    from euroleague_api.game_metadata import GameMetadata  # type: ignore

    boxscore_client = BoxScoreData()
    meta_client = GameMetadata()

    # Step 1: get all gamecodes for the season and filter to target round
    logger.info(f"Fetching game schedule for season {SEASON_CODE}...")
    season_df = boxscore_client.get_gamecodes_season(SEASON_CODE)
    round_games = season_df[
        (season_df["Round"] == round_number) & (season_df["played"] == True)  # noqa: E712
    ]

    if round_games.empty:
        raise ValueError(
            f"No played games found for round {round_number} in season {SEASON_CODE}. "
            "Either the round hasn't been played yet or the round number is wrong."
        )

    gamecodes = round_games["gameCode"].tolist()
    logger.info(f"Round {round_number}: found {len(gamecodes)} games — gamecodes {gamecodes}")

    all_player_stats = []
    coach_data = {}  # team_code -> {"team_code", "margin", "fantasy_points"}

    # Step 2: fetch player stats and coach data for each game
    for gc in gamecodes:
        logger.info(f"Fetching boxscore for gamecode {gc}...")
        try:
            df = boxscore_client.get_player_boxscore_stats_data(
                season=SEASON_CODE, gamecode=gc
            )
            if df is None or df.empty:
                logger.warning(f"Gamecode {gc} returned empty boxscore")
            else:
                # The API appends a "Total" summary row — exclude it
                df = df[df["Player_ID"] != "Total"]
                for row in df.to_dict(orient="records"):
                    mapped = _map_player_row(row)
                    mapped["fantasy_points"] = compute_fantasy_points(mapped)
                    all_player_stats.append(mapped)
        except Exception as e:
            logger.error(f"Failed to fetch boxscore for gamecode {gc}: {e}")

        # Fetch game result for coach scoring
        logger.info(f"Fetching game metadata for gamecode {gc}...")
        try:
            meta_df = meta_client.get_game_metadata(season=SEASON_CODE, gamecode=gc)
            row = meta_df.iloc[0]
            score_a = int(row["ScoreA"])
            score_b = int(row["ScoreB"])
            team_a = str(row["CodeTeamA"])
            team_b = str(row["CodeTeamB"])
            margin_a = score_a - score_b
            margin_b = score_b - score_a
            coach_data[team_a] = {
                "team_code": team_a,
                "coach_name": str(row.get("CoachA", "")),
                "margin": margin_a,
                "fantasy_points": compute_coach_fantasy_points(margin_a),
            }
            coach_data[team_b] = {
                "team_code": team_b,
                "coach_name": str(row.get("CoachB", "")),
                "margin": margin_b,
                "fantasy_points": compute_coach_fantasy_points(margin_b),
            }
        except Exception as e:
            logger.error(f"Failed to fetch metadata for gamecode {gc}: {e}")

    # Step 3: auto-match player IDs by name
    players = _load_players()
    if players:
        _update_player_ids(players, all_player_stats)

    return {
        "round": round_number,
        "players": all_player_stats,
        "coaches": list(coach_data.values()),
    }
