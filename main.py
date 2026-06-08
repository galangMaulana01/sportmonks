from fastapi import FastAPI
import httpx
import os

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"


@app.get("/")
async def root():
    return {"message": "active"}


@app.get("/leagues/{league_id}")
async def league(league_id: int):
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
                "api_token": SPORTMONKS_TOKEN,
                "include": "stages"
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/stages/{stage_id}")
async def stage(stage_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/stages/{stage_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )

        response.raise_for_status()
        return response.json()
        
@app.get("/rounds/{round_id}")
async def round(round_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/rounds/{round_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )

        response.raise_for_status()

        return response.json()
        
@app.get("/rounds/{round_id}/fixtures")
async def round_fixtures(round_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/rounds/{round_id}",
            params={
                "api_token": SPORTMONKS_TOKEN,
                "include": "fixtures"
            }
        )

        response.raise_for_status()

        return response.json()
        
@app.get("/standings/seasons/{season_id}")
async def standing(season_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/standings/seasons/{season_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()


@app.get("/teams/{team_id}")
async def team(team_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/teams/{team_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()

@app.get("/fixtures/date/{date}")
async def fixtures_by_date(date: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/fixtures/date/{date}",
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