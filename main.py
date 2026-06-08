from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"

@app.get("/")
async def root():
    return {
        "message": "active"
    }

@app.get("/leagues/{league_id}")
async def league_season(league_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/leagues/{league_id}",
            params={
                "api_token": SPORTMONKS_TOKEN,
                "include": "currentseason"
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/seasons/{season_id}")
async def season(season_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/seasons/{season_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/standings/seasons/{season_id}/")
async def season_standings(season_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/standings/seasons/{season_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/fixtures/{team_id}")
async def fixture(team_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/fixtures/{team_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/fixtures/{fixture_id}")
async def fixture(fixture_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/fixtures/{fixture_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()