import json
from fastapi import APIRouter, HTTPException
from config import STATS_DIR
from services import euroleague_api as api_service

router = APIRouter()


def _stats_path(round_number: int):
    return STATS_DIR / f"round_{round_number}.json"


@router.post("/stats/fetch/{round_number}")
def fetch_stats(round_number: int):
    """
    Fetch all game stats for a round from the Euroleague API,
    compute fantasy points, and save to data/stats/round_N.json.
    """
    data = api_service.fetch_round_stats(round_number)
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    path = _stats_path(round_number)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    player_count = len(data.get("players", []))
    coach_count = len(data.get("coaches", []))
    return {
        "message": f"Round {round_number} stats saved",
        "players_fetched": player_count,
        "coaches_fetched": coach_count,
    }


@router.get("/stats/round/{round_number}")
def get_round_stats(round_number: int):
    """Return all player fantasy points for a round, sorted descending."""
    path = _stats_path(round_number)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No stats for round {round_number}. Call POST /stats/fetch/{round_number} first.",
        )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    players = sorted(data.get("players", []), key=lambda p: p["fantasy_points"], reverse=True)
    return {
        "round": round_number,
        "players": players,
        "coaches": data.get("coaches", []),
    }
