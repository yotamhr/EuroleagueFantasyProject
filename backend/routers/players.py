import json
from fastapi import APIRouter, HTTPException, Query
from config import PLAYERS_FILE, COACHES_FILE

router = APIRouter()


def _load_json(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@router.get("/players")
def get_players(
    position: str | None = Query(None, description="Filter by position: G, F, or C"),
    team: str | None = Query(None, description="Filter by team code, e.g. MAD"),
    search: str | None = Query(None, description="Search by name (case-insensitive)"),
):
    players = _load_json(PLAYERS_FILE)
    if position:
        players = [p for p in players if p["position"].upper() == position.upper()]
    if team:
        players = [p for p in players if p["team_code"].upper() == team.upper()]
    if search:
        players = [p for p in players if search.lower() in p["name"].lower()]
    return players


@router.get("/players/{player_id}")
def get_player(player_id: int):
    players = _load_json(PLAYERS_FILE)
    for p in players:
        if p["id"] == player_id:
            return p
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found")


@router.get("/coaches")
def get_coaches():
    return _load_json(COACHES_FILE)
