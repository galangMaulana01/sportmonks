from fastapi import FastAPI, Query, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
import httpx  
import os  
from fastapi.responses import FileResponse
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
from motor.motor_asyncio import AsyncIOMotorClient
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import date, datetime

app = FastAPI()  

MONGODB_URI = os.getenv("MONGODB_URI")

mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client["bolaindo"]

settings_collection = db["settings"]
users_collection = db["users"]
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
  
class GoogleLogin(BaseModel):
    id_token: str
    
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

@app.post("/auth/google")
async def google_login(data: GoogleLogin, request: Request):

    try:
        info = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )

        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.client.host
        )

        user = {
            "google_id": info["sub"],
            "email": info["email"],
            "name": info.get("name"),
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "ip": client_ip
        }

        await users_collection.update_one(
            {"google_id": user["google_id"]},
            {
                "$set": {
                    "email": user["email"],
                    "name": user["name"],
                    "last_login": user["last_login"],
                    "ip": user["ip"]
                },
                "$setOnInsert": {
                    "created_at": user["created_at"],
                    "google_id": user["google_id"]
                }
            },
            upsert=True
        )

        return {
            "success": True,
            "user": {
                "google_id": user["google_id"],
                "email": user["email"],
                "name": user["name"]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Login Google gagal: {str(e)}"
        )
@app.get("/admin/users")
async def admin_users():

    users = []

    async for user in users_collection.find(
        {},
        {"_id": 0}
    ).sort("last_login", -1):

        users.append(user)

    return {
        "success": True,
        "users": users
    }
    
@app.get("/auth/google/login")
async def google_login_redirect():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&redirect_uri=https://sportmonks-tawny.vercel.app/auth/google/callback"
        "&access_type=offline"
        "&prompt=select_account"
    )
    return RedirectResponse(url=google_auth_url)