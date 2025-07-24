from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import re
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-_. ]", "", name)
    return name.replace(" ", "_")

def get_platform_options(platform: str) -> dict:
    base_opts = {
        'quiet': False,
        'no_playlist': True,
        'retries': 3,
    }
    user_agent_desktop = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    user_agent_mobile = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"

    if platform == "youtube":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'user_agent': user_agent_desktop,
        }
    elif platform in ["tiktok", "instagram"]:
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'user_agent': user_agent_mobile,
        }
    elif platform == "snapchat":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
        }

    return base_opts

@app.get("/")
async def root():
    return {"status": "active", "message": "Zyvid API läuft"}

@app.get("/download")
async def download_video(
    request: Request,
    url: str = Query(...),
    platform: str = Query("youtube")
):
    logger.info(f"Download angefragt: {url} (Plattform: {platform})")

    if not url or not url.startswith(("http://", "https://")):
        return {"status": "error", "message": "Ungültige URL"}

    ydl_opts = get_platform_options(platform)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
    except Exception as e:
        msg = str(e).lower()
        if "login" in msg or "sign in" in msg:
            return {"status": "error", "message": f"{platform.capitalize()} verlangt Login – derzeit nicht unterstützt."}
        if "unsupported url" in msg:
            return {"status": "error", "message": f"Diese {platform}-URL wird nicht unterstützt."}
        return {"status": "error", "message": f"Fehler beim Extrahieren: {str(e)}"}

    filename = f"{platform}_{sanitize_filename(title)}.{ext}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    download_opts = {
        **ydl_opts,
        'outtmpl': filepath
    }

    try:
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return {"status": "error", "message": f"Fehler beim Download: {str(e)}"}

    if not os.path.exists(filepath):
        return {"status": "error", "message": "Datei nicht gefunden"}

    return {
        "status": "success",
        "platform": platform,
        "title": title,
        "filename": filename,
        "download_url": f"{request.base_url}file/{filename}"
    }

@app.get("/file/{filename}")
async def serve_file(filename: str):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return FileResponse(
            path,
            media_type="video/mp4",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    return {"status": "error", "message": "Datei nicht gefunden"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "downloads_dir": DOWNLOAD_DIR,
        "exists": os.path.exists(DOWNLOAD_DIR)
    }
