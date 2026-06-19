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
from fastapi.responses import RedirectResponse
import secrets
import json
import urllib.parse
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
        {"include": "currentSeason;country;seasons"}  
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
    return await sportmonks_get(
        f"/teams/{team_id}",
        {"include": "venue"}
    )  
   
@app.get("/fixtures/{fixture_id}")  
async def fixture(fixture_id: int):  
    return await sportmonks_get(  
        f"/fixtures/{fixture_id}",  
        {"include": "participants;league;venue;state;scores;lineups.player;lineups.type;lineups.details.type;metadata.type;coaches;events.type;events.period;events.player;statistics.type;sidelined.sideline.player;sidelined.sideline.type;predictions.type"}
    )

@app.get("/livescores/inplay")
async def livescores_inplay(include: str = Query(None)):
    return await sportmonks_get(
        "/livescores/inplay",
        {"include": "participants;scores;periods;events;league.country;round;venue"}
    )
# New endpoints for v3 as per request

@app.get("/players/search/{query}")
async def search_players(query: str, include: str = Query(None), page: int = Query(1), per_page: int = Query(25)):
    params = {}
    if include:
        params["include"] = include
    params["page"] = page
    params["per_page"] = per_page
    return await sportmonks_get(f"/players/search/{query}", params)

from fastapi import Query
from typing import Optional

@app.get("/teams/search/{query}")
async def search_teams(
    query: str, 
    include: Optional[str] = Query(None), 
    page: int = Query(1), 
    per_page: int = Query(25)
):
    params = {
        "page": page,
        "per_page": per_page
    }
    if include:
        params["include"] = include
        
    return await sportmonks_get(f"/teams/search/{query}", params)

@app.get("/leagues")  
async def get_all_leagues():  
    return await sportmonks_get(
        f"/leagues"
    )
    
@app.get("/leagues/search/{query}")
async def search_leagues(query: str, include: str = Query(None), page: int = Query(1), per_page: int = Query(25)):
    params = {}
    if include:
        params["include"] = include
    params["page"] = page
    params["per_page"] = per_page
    return await sportmonks_get(f"/leagues/search/{query}", params)

@app.get("/fixtures/date/{date}")
async def fixtures_by_date(date: str, include: str = Query(None), page: int = Query(1), per_page: int = Query(25)):
    params = {}
    if include:
        params["include"] = include
    params["page"] = page
    params["per_page"] = per_page
    return await sportmonks_get(f"/fixtures/date/{date}", params)

@app.get("/squads/teams/{team_id}")
async def squads_by_team(team_id: int):
    return await sportmonks_get(
        f"/squads/teams/{team_id}",
        {"include": "team;player.nationality;player.statistics.details.type;player.position"}
    )

@app.get("/standings/live/leagues/{league_id}")
async def live_standings(league_id: int, include: str = Query(None)):
    params = {}
    if include:
        params["include"] = include
    return await sportmonks_get(f"/standings/live/leagues/{league_id}", params)

@app.get("/topscorers/seasons/{season_id}")
async def topscorers(season_id: int, include: str = Query(None)):
    params = {}
    if include:
        params["include"] = include
    return await sportmonks_get(f"/topscorers/seasons/{season_id}", params)

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
     
# ==================== GOOGLE OAUTH SERVER-SIDE FLOW ====================

@app.get("/auth/google/login")
async def google_login_redirect(request: Request):
    """Redirect user ke Google OAuth (fallback jika One Tap gagal)"""
    # Simpan state untuk mencegah CSRF
    state = secrets.token_urlsafe(32)
    # Simpan di session/cookie sederhana (kita pakai memory sederhana, atau bisa pakai Redis/DB)
    # Untuk sederhana, kita kirim sebagai query param di redirect_uri
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        f"&redirect_uri=https://sportmonks-tawny.vercel.app/auth/google/callback"
        "&access_type=offline"
        "&prompt=select_account"
        f"&state={state}"
    )
    return RedirectResponse(url=google_auth_url)


@app.get("/auth/google/callback")
async def google_login_callback(code: str, request: Request):
    """Callback dari Google, menukar code dengan token"""
    try:
        # Tukar authorization code dengan token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),  # Pastikan ini ada di env!
                    "redirect_uri": "https://sportmonks-tawny.vercel.app/auth/google/callback",
                    "grant_type": "authorization_code"
                }
            )
            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(status_code=400, detail=f"Google token error: {token_data.get('error_description', token_data['error'])}")
            
            id_token_jwt = token_data.get("id_token")
            if not id_token_jwt:
                raise HTTPException(status_code=400, detail="No id_token received")
            
            # Verifikasi ID Token
            info = id_token.verify_oauth2_token(
                id_token_jwt,
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
            
            user_data = {
                "google_id": user["google_id"],
                "email": user["email"],
                "name": user["name"]
            }

            user_json = urllib.parse.quote(json.dumps(user_data))
            frontend_url = f"capacitor://localhost/#auth_success={user_json}"
            return RedirectResponse(url=frontend_url)

    except Exception as e:
        error_msg = str(e)
        return RedirectResponse(url=f"capacitor://localhost/#auth_error={error_msg[:100]}")
        
class NativeGoogleUser(BaseModel):
    google_id: str
    email: str
    name: str

@app.post("/auth/google-native")
async def google_native_login(data: NativeGoogleUser, request: Request):
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host
    )
    
    await users_collection.update_one(
        {"google_id": data.google_id},
        {
            "$set": {
                "email": data.email,
                "name": data.name,
                "last_login": datetime.utcnow(),
                "ip": client_ip
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow(),
                "google_id": data.google_id
            }
        },
        upsert=True
    )
    
    return {"success": True, "user": {"google_id": data.google_id, "email": data.email, "name": data.name}}
