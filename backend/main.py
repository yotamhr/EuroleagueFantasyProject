from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import players, squad, stats, breakdown

app = FastAPI(title="Euroleague Fantasy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(squad.router)
app.include_router(stats.router)
app.include_router(breakdown.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Euroleague Fantasy API"}
