from fastapi import FastAPI, Query
import httpx
import os
from datetime import date

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"

async def sportmonks_get(path: str, params: dict = {}):
    params["api_token"] = SPORTMONKS_TOKEN
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE_URL}{path}", params=params)
        r.raise_for_status()
        return r.json()

@app.get("/")
async def root():
    return {"message": "active"}

@app.get("/leagues/{league_id}")
async def league(league_id: int):
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

@app.get("/fixtures/{fixture_id}")
async def fixture(fixture_id: int):
    return await sportmonks_get(
        f"/fixtures/{fixture_id}",
        {"include": "participants;scores;events;lineups;state;periods;formations;statistics.type"}
    )

# top score

@app.get("/topscorers/seasons/{season_id}")
async def topscorers_season(season_id: int):
    return await sportmonks_get(f"/topscorers/seasons/{season_id}")

# schedule

@app.get("/schedules/seasons/{season_id}")
async def schedule_by_season(season_id: int):
    return await sportmonks_get(f"/schedules/seasons/{season_id}")

@app.get("/schedules/teams/{team_id}")
async def schedule_by_team(team_id: int):
    return await sportmonks_get(f"/schedules/teams/{team_id}")
    