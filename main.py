from fastapi import FastAPI
import httpx
import os

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"


@app.get("/")
async def root():
    return {
        "message": "API Ready"
    }


@app.get("/league/{league_id}")
async def league(league_id: int):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/leagues/{league_id}",
            params={
                "api_token": SPORTMONKS_TOKEN
            }
        )

        response.raise_for_status()

        return response.json()
        
        
@app.get("/league/{league_id}/season")
async def league_season(league_id: int):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/leagues/{league_id}",
            params={
                "api_token": SPORTMONKS_TOKEN,
                "include": "currentSeason"
            }
        )

        response.raise_for_status()

        return response.json()
        

@app.get("/league/{league_id}/fixtures")
async def league_fixtures(league_id: int):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/fixtures",
            params={
                "api_token": SPORTMONKS_TOKEN,
                "filters": f"leagueId:{league_id}"
            }
        )

        response.raise_for_status()

        return response.json()