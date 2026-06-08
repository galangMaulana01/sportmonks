from fastapi import FastAPI, HTTPException
from services.sportmonks import get_league

app = FastAPI()


@app.get("/")
async def league(id: int):
    try:
        data = await get_league(id)

        return {
            "success": True,
            "data": data["data"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )