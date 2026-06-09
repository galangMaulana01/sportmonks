from fastapi import FastAPI, Query, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware  
import httpx  
import os  
from datetime import date  
from fastapi.responses import FileResponse
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
from motor.motor_asyncio import AsyncIOMotorClient


app = FastAPI()  

MONGODB_URI = os.getenv("MONGODB_URI")

mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client["bolaindo"]
settings_collection = db["settings"]
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  
  
SPORTMONKS_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")  
BASE_URL = "https://api.sportmonks.com/v3/football"  
  
class Banner(BaseModel):
    image_benner: str
    image_logo: str
    desc: str
    link: str
  
async def sportmonks_get(path: str, params: dict = {}):  
    params["api_token"] = SPORTMONKS_TOKEN  
    async with httpx.AsyncClient(timeout=15) as client:  
        r = await client.get(f"{BASE_URL}{path}", params=params)  
        r.raise_for_status()  
        return r.json()  
  
@app.get("/")  
async def root():  
    return {"message": "active"}  
  
@app.get("/benner")
async def benner():

    banner = await settings_collection.find_one(
        {"type": "banner"},
        {"_id": 0}
    )

    if banner:
        return banner

    return {
        "image_benner": "",
        "image_logo": "",
        "desc": "",
        "link": ""
    }
    
@app.get("/admin")
async def admin():
    return FileResponse("src/index.html")

@app.get("/db-check")
async def check_db_connection():
    try:
        # Kirim perintah 'ping' ke MongoDB buat mastiin koneksi jalan
        await mongo_client.admin.command('ping')
        
        return {
            "status": "success", 
            "message": "Mantap bro, Database MongoDB berhasil connect!"
        }
    except Exception as e:
        # Kalau gagal connect, bakal return error 500 beserta pesan error aslinya
        raise HTTPException(
            status_code=500, 
            detail=f"Waduh, Database gagal connect bro: {str(e)}"
        )
        
@app.post("/admin/benner")
async def update_banner(data: Banner):

    payload = {
        "type": "banner",
        **data.dict()
    }

    await settings_collection.update_one(
        {"type": "banner"},
        {"$set": payload},
        upsert=True
    )

    return {
        "success": True,
        "data": payload
    }

@app.post("/admin/upload")
async def upload_image(file: UploadFile = File(...)):
    result = cloudinary.uploader.upload(
        file.file,
        folder="bolaindo"
    )

    return {
        "success": True,
        "url": result["secure_url"]
    }
    

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
    return await sportmonks_get(
        f"/standings/seasons/{season_id}",
        {"include": "participant;rule.type;details.type;form;stage;league;group"}
    )  
    
@app.get("/squads/seasons/{season_id}/teams/{team_id}")
async def squads(season_id: int,team_id: int):  
    return await sportmonks_get(
        f"/squads/seasons/{season_id}/teams/{team_id}",
        {"include": "team;player.nationality;details.type;player.position"}
    )  
    
@app.get("/teams/{team_id}")  
async def team(team_id: int):  
    return await sportmonks_get(f"/teams/{team_id}")  
  
@app.get("/fixtures/{fixture_id}")  
async def fixture(fixture_id: int):  
    return await sportmonks_get(  
        f"/fixtures/{fixture_id}",  
        {"include": "participants;league;venue;state;scores;lineups.player;lineups.type;lineups.details.type;metadata.type;coaches;events.type;events.period;events.player;statistics.type;sidelined.sideline.player;sidelined.sideline.type"}
    )
