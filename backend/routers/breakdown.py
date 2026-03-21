import json
from fastapi import APIRouter, HTTPException
from config import SQUADS_DIR, STATS_DIR, PLAYERS_FILE, COACHES_FILE

router = APIRouter()


def _load_json(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _players_by_id(players_list: list) -> dict:
    return {p["id"]: p for p in players_list}


def _stats_by_euroleague_id(players_stats: list) -> dict:
    return {p["player_euroleague_id"]: p for p in players_stats}


@router.get("/squad/{round_number}/breakdown")
def get_breakdown(round_number: int):
    """
    Return per-player fantasy point contributions for the user's squad,
    applying the bench 50% rule, auto-sub, and captain/vice-captain doubling.
    """
    # Load squad
    squad_path = SQUADS_DIR / f"round_{round_number}.json"
    if not squad_path.exists():
        raise HTTPException(status_code=404, detail=f"No squad saved for round {round_number}")
    with open(squad_path, encoding="utf-8") as f:
        squad = json.load(f)

    # Load stats
    stats_path = STATS_DIR / f"round_{round_number}.json"
    if not stats_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No stats for round {round_number}. Fetch stats first.",
        )
    with open(stats_path, encoding="utf-8") as f:
        stats_data = json.load(f)

    # Load player metadata (to find euroleague_player_id by our id)
    all_players = _load_json(PLAYERS_FILE)
    players_by_id = _players_by_id(all_players)

    # Index stats by euroleague_player_id
    stats_by_elid = _stats_by_euroleague_id(stats_data.get("players", []))

    captain_id = squad.get("captain_id")
    vice_captain_id = squad.get("vice_captain_id")

    def get_player_stats(player_id: int) -> dict | None:
        player = players_by_id.get(player_id)
        if not player:
            return None
        el_id = player.get("euroleague_player_id")
        if not el_id:
            return None
        return stats_by_elid.get(el_id)

    def did_play(player_id: int) -> bool:
        st = get_player_stats(player_id)
        if st is None:
            return False
        minutes = st.get("minutes_played", "00:00")
        return minutes != "00:00" and minutes != ""

    def raw_points(player_id: int) -> float:
        st = get_player_stats(player_id)
        if st is None:
            return 0.0
        return st.get("fantasy_points", 0.0)

    # Build a map: position_slot -> bench player_id
    bench_by_pos = {}
    for slot in squad.get("bench", []):
        bench_by_pos[slot["position_slot"]] = slot["player_id"]

    contributions = []
    captain_played = did_play(captain_id) if captain_id else False

    for slot in squad.get("starters", []):
        pid = slot["player_id"]
        pos = slot["position_slot"]
        player_info = players_by_id.get(pid, {})
        played = did_play(pid)
        points = raw_points(pid)

        if not played:
            # Auto-sub: bench player at same position plays instead (at 100%)
            bench_pid = bench_by_pos.get(pos)
            if bench_pid and did_play(bench_pid):
                bench_info = players_by_id.get(bench_pid, {})
                bench_points = raw_points(bench_pid)
                note = "auto-sub"

                # Captain logic applies to the subbed-in bench player only if
                # the captain slot was the starter who didn't play
                multiplier = 1.0
                if pid == captain_id and not captain_played:
                    if vice_captain_id and did_play(vice_captain_id):
                        pass  # vice-captain handles their own doubling below
                    else:
                        multiplier = 2.0  # bench sub inherits captain role
                        note = "auto-sub + captain"

                contributions.append({
                    "player_id": bench_pid,
                    "name": bench_info.get("name", f"Player {bench_pid}"),
                    "position_slot": pos,
                    "role": "bench (auto-sub)",
                    "raw_fantasy_points": bench_points,
                    "multiplier": multiplier,
                    "contributed_points": round(bench_points * multiplier, 2),
                    "note": note,
                })
            else:
                # Neither starter nor bench sub played — 0 points
                contributions.append({
                    "player_id": pid,
                    "name": player_info.get("name", f"Player {pid}"),
                    "position_slot": pos,
                    "role": "starter (did not play)",
                    "raw_fantasy_points": 0.0,
                    "multiplier": 1.0,
                    "contributed_points": 0.0,
                    "note": "no sub available",
                })
        else:
            # Starter played normally
            multiplier = 1.0
            note = ""
            if pid == captain_id and captain_played:
                multiplier = 2.0
                note = "captain"
            elif pid == vice_captain_id and not captain_played:
                multiplier = 2.0
                note = "vice-captain (acting captain)"

            contributions.append({
                "player_id": pid,
                "name": player_info.get("name", f"Player {pid}"),
                "position_slot": pos,
                "role": "starter",
                "raw_fantasy_points": points,
                "multiplier": multiplier,
                "contributed_points": round(points * multiplier, 2),
                "note": note,
            })

    # Bench players (not used as auto-subs already handled above)
    starters_not_played = {
        slot["position_slot"]
        for slot in squad.get("starters", [])
        if not did_play(slot["player_id"])
    }
    for slot in squad.get("bench", []):
        pid = slot["player_id"]
        pos = slot["position_slot"]
        player_info = players_by_id.get(pid, {})
        points = raw_points(pid)

        # If this bench player was already used as auto-sub, they're already counted
        already_used = pos in starters_not_played and did_play(pid)
        if already_used:
            continue  # already accounted for above

        contributions.append({
            "player_id": pid,
            "name": player_info.get("name", f"Player {pid}"),
            "position_slot": pos,
            "role": "bench",
            "raw_fantasy_points": points,
            "multiplier": 0.5,
            "contributed_points": round(points * 0.5, 2),
            "note": "bench (50%)",
        })

    # Coach
    coach_id = squad.get("coach_id")
    coach_points = 0.0
    coach_name = f"Coach {coach_id}"
    if coach_id:
        all_coaches = _load_json(COACHES_FILE)
        coach_map = {c["id"]: c for c in all_coaches}
        coach_info = coach_map.get(coach_id, {})
        coach_name = coach_info.get("name", coach_name)
        team_code = coach_info.get("team_code", "")
        for cs in stats_data.get("coaches", []):
            if cs.get("team_code", "").upper() == team_code.upper():
                coach_points = cs.get("fantasy_points", 0.0)
                break

    total = sum(c["contributed_points"] for c in contributions) + coach_points

    return {
        "round": round_number,
        "contributions": contributions,
        "coach": {
            "coach_id": coach_id,
            "name": coach_name,
            "fantasy_points": coach_points,
        },
        "total_fantasy_points": round(total, 2),
    }
