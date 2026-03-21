# Euroleague Fantasy Project

A personal web app for the Israeli Euroleague fantasy basketball game (ערוץ הספורט). Fetches real Euroleague stats, calculates fantasy points, and helps optimize team selection.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yotamhr/EuroleagueFantasyProject.git
cd EuroleagueFantasyProject
```

### 2. Backend
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Frontend
```bash
cd frontend
npm install
```

## Running the App

**Terminal 1 — Backend:**
```bash
.venv\Scripts\activate   # or source .venv/bin/activate
cd backend
uvicorn main:app --reload
```
API runs at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
App runs at `http://localhost:5173`

## Player Data

The file `data/players.json` contains the player list with prices and positions for the current season. Edit this file to update player data. The `euroleague_player_id` field is filled in automatically on the first stats fetch.

## Usage

1. **Fetch round stats:** Go to the Stats page, enter a round number, click "Fetch from API"
2. **Set your squad:** Go to My Squad page, set your team for the round
3. **View breakdown:** See your squad's total fantasy points with per-player breakdown

## Project Structure

See `CLAUDE.md` for full technical context (relevant if working with Claude Code AI assistant).
