import os
import httpx

API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"


async def get_league(league_id: int):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{BASE_URL}/leagues/{league_id}",
            params={
                "api_token": API_TOKEN,
            },
        )

        response.raise_for_status()

        return response.json()