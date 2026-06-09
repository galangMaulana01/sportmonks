from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# ======================
# CORS
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# CONFIG
# ======================
SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.sportcache


# ======================
# HTTP CLIENT
# ======================
async def sportmonks_get(path: str, params: dict = None):
    if params is None:
        params = {}

    params["api_token"] = SPORTMONKS_TOKEN

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE_URL}{path}", params=params)
        r.raise_for_status()
        return r.json()


# ======================
# MONGO CACHE
# ======================
async def set_cache(key: str, data: dict):
    await db.cache_data.update_one(
        {"key": key},
        {
            "$set": {
                "key": key,
                "data": data,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )


async def get_cache(key: str):
    return await db.cache_data.find_one({"key": key})


# ======================
# ROOT
# ======================
@app.get("/")
async def root():
    return {"message": "API active"}


# =========================================================
# LEAGUES
# =========================================================
@app.get("/leagues/{league_id}")
async def league(league_id: int):
    key = f"league_{league_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(
        f"/leagues/{league_id}",
        {"include": "currentSeason;country"}
    )

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# SEASONS
# =========================================================
@app.get("/seasons/{season_id}")
async def season(season_id: int):
    key = f"season_{season_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(
        f"/seasons/{season_id}",
        {"include": "stages;currentStage"}
    )

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# STAGES
# =========================================================
@app.get("/stages/{stage_id}")
async def stage(stage_id: int):
    key = f"stage_{stage_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(
        f"/stages/{stage_id}",
        {"include": "rounds;currentRound"}
    )

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# ROUNDS
# =========================================================
@app.get("/rounds/{round_id}")
async def round(round_id: int):
    key = f"round_{round_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(
        f"/rounds/{round_id}",
        {"include": "fixtures"}
    )

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# STANDINGS
# =========================================================
@app.get("/standings/{season_id}")
async def standings(season_id: int):
    key = f"standings_{season_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(f"/standings/seasons/{season_id}")

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# TEAMS
# =========================================================
@app.get("/teams/{team_id}")
async def team(team_id: int):
    key = f"team_{team_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(f"/teams/{team_id}")

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# FIXTURES (FULL DETAIL)
# =========================================================
@app.get("/fixtures/{fixture_id}")
async def fixture(fixture_id: int):
    key = f"fixture_{fixture_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(
        f"/fixtures/{fixture_id}",
        {
            "include": "participants;scores;events;lineups;state;periods;formations;statistics.type;venue;league;season;stage;round"
        }
    )

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# TOP SCORERS
# =========================================================
@app.get("/topscorers/{season_id}")
async def topscorers(season_id: int):
    key = f"topscorers_{season_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(f"/topscorers/seasons/{season_id}")

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# SCHEDULES
# =========================================================
@app.get("/schedules/seasons/{season_id}")
async def schedule_season(season_id: int):
    key = f"schedule_season_{season_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(f"/schedules/seasons/{season_id}")

    await set_cache(key, data)
    return {"source": "api", "data": data}


@app.get("/schedules/teams/{team_id}")
async def schedule_team(team_id: int):
    key = f"schedule_team_{team_id}"

    cache = await get_cache(key)
    if cache:
        return {"source": "cache", "data": cache["data"]}

    data = await sportmonks_get(f"/schedules/teams/{team_id}")

    await set_cache(key, data)
    return {"source": "api", "data": data}


# =========================================================
# 🔥 INIT SYNC (BIAR DB LANGSUNG KEISI)
# =========================================================
async def sync_all():
    print("SYNC START...")

    season_ids = [2023, 2024]

    for season_id in season_ids:

        standings = await sportmonks_get(f"/standings/seasons/{season_id}")
        await set_cache(f"standings_{season_id}", standings)

        topscorers = await sportmonks_get(f"/topscorers/seasons/{season_id}")
        await set_cache(f"topscorers_{season_id}", topscorers)

        fixtures = await sportmonks_get(f"/fixtures/date/2026-06-09")
        await set_cache(f"fixtures_{season_id}", fixtures)

    print("SYNC DONE")


# =========================================================
# STARTUP AUTO SYNC
# =========================================================
@app.on_event("startup")
async def startup():
    await sync_all()


# =========================================================
# MANUAL SYNC
# =========================================================
@app.get("/sync-now")
async def sync_now():
    await sync_all()
    return {"message": "sync completed"}