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