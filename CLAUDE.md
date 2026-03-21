# Euroleague Fantasy Project — Claude Context

## What This Project Is
A personal web app to assist with the Israeli sports channel (ערוץ הספורט) Euroleague basketball fantasy game. The app fetches real Euroleague stats, calculates fantasy points, tracks the user's squad, and will eventually optimize team selection.

## Tech Stack
- **Backend:** Python + FastAPI, JSON files for storage (no database in MVP)
- **Frontend:** React + Vite + TypeScript
- **Stats source:** `euroleague-api` PyPI package, season code `E2025` (2025-26 season)
- **Optimization (future):** PuLP (integer linear programming)

## How to Run

### Backend
```bash
# From project root — first time only
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r backend/requirements.txt

# Every time
.venv\Scripts\activate
cd backend
uvicorn main:app --reload
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install   # first time only
npm run dev
# Runs at http://localhost:5173
```

## Project Structure
```
EuroleagueFantasyProject/
├── backend/
│   ├── main.py                 # FastAPI app, CORS config
│   ├── config.py               # SEASON_CODE=2025, file paths
│   ├── routers/
│   │   ├── players.py          # GET /players, GET /coaches
│   │   ├── squad.py            # GET/PUT /squad/{round}
│   │   ├── stats.py            # POST /stats/fetch/{round}, GET /stats/round/{round}
│   │   └── breakdown.py        # GET /squad/{round}/breakdown
│   └── services/
│       ├── euroleague_api.py   # Wraps euroleague-api package; fetches round stats
│       └── fantasy_scorer.py  # Fantasy point formula
├── frontend/src/
│   ├── api/client.ts           # Axios wrappers for all endpoints
│   ├── pages/
│   │   ├── StatsPage.tsx       # Round stats table (fetch + view)
│   │   └── SquadPage.tsx       # Squad breakdown view
│   └── App.tsx                 # Router + nav
├── data/
│   ├── players.json            # Player list: {id, name, position, team_code, price, euroleague_player_id}
│   ├── coaches.json            # Coach list: {id, name, team_code, price}
│   ├── squads/round_N.json     # User's squad per round (committed to git)
│   └── stats/round_N.json      # Fetched stats per round (gitignored, re-fetchable)
└── scripts/
    └── explore_api.py          # Exploration/testing script for the euroleague-api package
```

## Game Rules (critical — every feature depends on these)

**Budget:** 100M NIS. **Roster:** 8 players + 1 coach.

**Starting 5:** 2 Guards (G), 2 Forwards (F), 1 Center (C)
**Bench 3:** 1G, 1F, 1C — contribute **50% of fantasy points**
**Auto-sub:** If a starter didn't play (`minutes == "00:00"`), their bench counterpart at the same position plays at **100%** instead.

**Captain** (starter only): points **doubled** (including negatives).
**Vice-captain** (starter only): doubles if captain didn't play.

**Transfers:** Max 3/round including coach swap. Do not accumulate.
**Team limit:** Max 2 players+coach from the same Euroleague team (regular season).

### Player Scoring Formula
```
+1  per point scored
+2  per rebound
+2  per assist
+3  per steal
+3  per block
+1  per foul drawn
-2  per turnover
-1  per missed shot (2pt, 3pt, or FT)
-1  per foul committed
+10 double-double bonus (10+ in 2 of: pts/reb/ast/stl/blk)
+20 triple-double bonus (10+ in 3 of: pts/reb/ast/stl/blk)
```

### Coach Scoring
```
Win:  +5 + winning margin
Loss: -5 - losing margin
```

## Euroleague API — Key Facts
- Package: `euroleague-api` (PyPI), class `BoxScoreData` (capital S)
- Season 2025-26 = season code `2025` in the package (not "E2025")
- `get_gamecodes_season(2025)` → all gamecodes + round numbers for the season
- `get_player_boxscore_stats_data(season=2025, gamecode=N)` → player stats DataFrame
- `GameMetadata().get_game_metadata(season=2025, gamecode=N)` → game result (scores, coaches)
- API column `Points` (not `Score`), `FoulsCommited` (one 't' — API typo)
- The DataFrame includes a "Total" summary row with `Player_ID == "Total"` — always filter it out
- Round 1 of E2025: gamecodes 1-10. Regular season has 10 games per round.

## Data Files
- `data/players.json` and `data/coaches.json` — source of truth, manually maintained
- `euroleague_player_id` in players.json starts as `null`, gets auto-filled on first stats fetch by name-matching
- Stats files are gitignored (auto-generated), squad files are committed

## What's Done (MVP)
- [x] All backend endpoints (players, coaches, squad CRUD, stats fetch, squad breakdown)
- [x] Fantasy scoring formula with double/triple-double detection
- [x] Euroleague API integration with correct field mapping
- [x] Squad breakdown with auto-sub, captain doubling, bench 50% rules
- [x] Basic React frontend (StatsPage, SquadPage)
- [x] API exploration script confirmed working for E2025

## What's Next (see GitHub Issues)
1. Add real player/coach data to JSON files
2. Test full round stats fetch end-to-end
3. Improve React UI (squad editing, player picker)
4. Add team optimizer (PuLP linear programming)
5. Add transfer suggester
6. Add captain recommendation algorithm
