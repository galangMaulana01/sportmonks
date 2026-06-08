from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3/football"


@app.get("/")
async def root():
    return {
        "message": "Sportmonks API Ready"
    }


@app.get("/league/{league_id}")
async def league(league_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/leagues/{league_id}",
                params={
                    "api_token": SPORTMONKS_TOKEN
                }
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/league/{league_id}/season")
async def league_season(league_id: int):
    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/season/{season_id}")
async def season(season_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/seasons/{season_id}",
                params={
                    "api_token": SPORTMONKS_TOKEN
                }
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/season/{season_id}/standings")
async def season_standings(season_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/standings/seasons/{season_id}",
                params={
                    "api_token": SPORTMONKS_TOKEN
                }
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/team/{team_id}")
async def team(team_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/teams/{team_id}",
                params={
                    "api_token": SPORTMONKS_TOKEN
                }
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/fixture/{fixture_id}")
async def fixture(fixture_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/fixtures/{fixture_id}",
                params={
                    "api_token": SPORTMONKS_TOKEN
                }
            )

            response.raise_for_status()

            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )