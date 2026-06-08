from fastapi import FastAPI, Query
import httpx
import os
from datetime import date

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"

# ─── Helper ───────────────────────────────────────────────
async def sportmonks_get(path: str, params: dict = {}):
    params["api_token"] = SPORTMONKS_TOKEN
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE_URL}{path}", params=params)
        r.raise_for_status()
        return r.json()


# ─── Existing Endpoints (dengan perbaikan) ─────────────────

@app.get("/")
async def root():
    return {"message": "active"}

@app.get("/leagues/{league_id}")
async def league(league_id: int):
    # Tambah stages untuk tahu stage aktif langsung
    return await sportmonks_get(
        f"/leagues/{league_id}",
        {"include": "currentSeason;country"}
    )

@app.get("/seasons/{season_id}")
async def season(season_id: int):
    return await sportmonks_get(
        f"/seasons/{season_id}",
        {"include": "stages;currentStage"}
    )

@app.get("/stages/{stage_id}")
async def stage(stage_id: int):
    # Tambah currentRound agar bisa langsung jump ke round aktif
    return await sportmonks_get(
        f"/stages/{stage_id}",
        {"include": "rounds;currentRound"}
    )

@app.get("/rounds/{round_id}")
async def round(round_id: int):
    return await sportmonks_get(
        f"/rounds/{round_id}",
        {"include": "fixtures"}
    )

@app.get("/standings/seasons/{season_id}")
async def standing(season_id: int):
    return await sportmonks_get(f"/standings/seasons/{season_id}")

@app.get("/teams/{team_id}")
async def team(team_id: int):
    return await sportmonks_get(f"/teams/{team_id}")

# Fixture detail dengan include livescore lengkap
@app.get("/fixtures/{fixture_id}")
async def fixture(fixture_id: int):
    return await sportmonks_get(
        f"/fixtures/{fixture_id}",
        {"include": "participants;scores;events;lineups;state;periods;formations"}
    )


# ─── NEW: Livescore Endpoints ──────────────────────────────

# Semua fixture live sekarang (inplay)
@app.get("/livescores/inplay")
async def livescores_inplay():
    return await sportmonks_get(
        "/livescores/inplay",
        {"include": "participants;scores;events;state;periods"}
    )

# Fixture 15 menit sebelum & setelah game (broader livescore)
@app.get("/livescores")
async def livescores_all():
    return await sportmonks_get(
        "/livescores",
        {"include": "participants;scores;state"}
    )

# Polling endpoint: fixture yang update dalam 10 detik terakhir
@app.get("/livescores/latest")
async def livescores_latest():
    return await sportmonks_get(
        "/livescores/latest",
        {"include": "participants;scores;events;state"}
    )


# ─── NEW: Fixture by Date ──────────────────────────────────

@app.get("/fixtures/date/{match_date}")
async def fixtures_by_date(match_date: str):
    # match_date format: YYYY-MM-DD
    return await sportmonks_get(
        f"/fixtures/date/{match_date}",
        {"include": "participants;scores;state;league"}
    )

@app.get("/fixtures/today")
async def fixtures_today():
    today = date.today().isoformat()
    return await sportmonks_get(
        f"/fixtures/date/{today}",
        {"include": "participants;scores;state;league"}
    )

@app.get("/fixtures/daterange/{start}/{end}")
async def fixtures_daterange(start: str, end: str):
    return await sportmonks_get(
        f"/fixtures/between/{start}/{end}",
        {"include": "participants;scores;state"}
    )


# ─── NEW: Topscorers ───────────────────────────────────────

@app.get("/topscorers/seasons/{season_id}")
async def topscorers_season(season_id: int):
    return await sportmonks_get(f"/topscorers/seasons/{season_id}")


# ─── NEW: Rounds by Season ─────────────────────────────────

@app.get("/rounds/seasons/{season_id}")
async def rounds_by_season(season_id: int):
    return await sportmonks_get(
        f"/rounds/seasons/{season_id}",
        {"include": "fixtures"}
    )


# ─── NEW: Schedules ────────────────────────────────────────

@app.get("/schedules/seasons/{season_id}")
async def schedule_by_season(season_id: int):
    return await sportmonks_get(f"/schedules/seasons/{season_id}")

@app.get("/schedules/teams/{team_id}")
async def schedule_by_team(team_id: int):
    return await sportmonks_get(f"/schedules/teams/{team_id}")