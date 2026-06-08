from fastapi import FastAPI
from services.sportmonks import get_league

app = FastAPI()


@app.get("/")
async def root():
    return {
        "status": "ok"
    }


@app.get("/league/{league_id}")
async def league(league_id: int):
    result = await get_league(league_id)

    return result