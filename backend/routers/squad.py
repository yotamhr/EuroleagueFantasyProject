import json
from fastapi import APIRouter, HTTPException
from config import SQUADS_DIR

router = APIRouter()


def _squad_path(round_number: int):
    return SQUADS_DIR / f"round_{round_number}.json"


@router.get("/squad/{round_number}")
def get_squad(round_number: int):
    path = _squad_path(round_number)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No squad saved for round {round_number}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@router.put("/squad/{round_number}")
def save_squad(round_number: int, body: dict):
    """
    Save the user's squad for a given round.

    Expected body:
    {
      "round": 1,
      "starters": [
        {"player_id": 5, "position_slot": "G"},
        {"player_id": 12, "position_slot": "G"},
        {"player_id": 3,  "position_slot": "F"},
        {"player_id": 8,  "position_slot": "F"},
        {"player_id": 1,  "position_slot": "C"}
      ],
      "bench": [
        {"player_id": 22, "position_slot": "G"},
        {"player_id": 17, "position_slot": "F"},
        {"player_id": 9,  "position_slot": "C"}
      ],
      "coach_id": 2,
      "captain_id": 5,
      "vice_captain_id": 12
    }
    """
    body["round"] = round_number
    SQUADS_DIR.mkdir(parents=True, exist_ok=True)
    path = _squad_path(round_number)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False, indent=2)
    return {"message": f"Squad saved for round {round_number}", "squad": body}
