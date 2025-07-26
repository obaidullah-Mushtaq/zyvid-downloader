from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import re
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

# Thread Pool für Downloads
executor = ThreadPoolExecutor(max_workers=4)

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-_. ]", "", name)
    return name.replace(" ", "_")

def get_platform_options(platform: str) -> dict:
    base_opts = {
        'quiet': True,
        'no_warnings': True,
        'no_playlist': True,
        'retries': 5,
        'fragment_retries': 5,
        'timeout': 30,
        'socket_timeout': 30,
    }

    if platform == "tiktok":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
            'http_headers': {
                'Referer': 'https://www.tiktok.com/',
            }
        }
    elif platform == "snapchat":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
        }
    elif platform == "pinterest":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
        }
    elif platform == "amazon":
        return {
            **base_opts,
            'format': 'bestvideo+bestaudio/best',
        }

    return base_opts

def extract_video_info(url: str, platform: str):
    """Video-Info extrahieren in separatem Thread"""
    ydl_opts = get_platform_options(platform)
    ydl_opts['quiet'] = True
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'success': True,
                'title': info.get("title", "video"),
                'ext': info.get("ext", "mp4"),
                'duration': info.get("duration"),
                'uploader': info.get("uploader")
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def download_video(url: str, platform: str, filepath: str):
    """Video herunterladen in separatem Thread"""
    ydl_opts = get_platform_options(platform)
    ydl_opts['outtmpl'] = filepath
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.get("/")
async def root():
    return {"status": "active", "message": "Zyvid API läuft"}

# ... alles unverändert bis download_video_endpoint()

@app.get("/download")
async def download_video_endpoint(
    request: Request,
    url: str = Query(...),
    platform: str = Query("youtube")
):
    logger.info(f"Download angefragt: {url} (Plattform: {platform})")

    if not url or not url.startswith(("http://", "https://")):
        return {"status": "error", "message": "Ungültige URL"}

    loop = asyncio.get_event_loop()



    # === Standard-Ablauf für andere Plattformen ===
    info_result = await loop.run_in_executor(executor, extract_video_info, url, platform)

    if not info_result['success']:
        error_msg = info_result['error'].lower()
        if "login" in error_msg or "sign in" in error_msg:
            return {"status": "error", "message": f"{platform.capitalize()} verlangt Login – derzeit nicht unterstützt."}
        if "unsupported url" in error_msg or "not supported" in error_msg:
            return {"status": "error", "message": f"Diese {platform}-URL wird nicht unterstützt."}
        if "private" in error_msg or "unavailable" in error_msg:
            return {"status": "error", "message": "Video ist privat oder nicht verfügbar."}
        return {"status": "error", "message": f"Fehler beim Extrahieren: {info_result['error'][:100]}"}

    title = info_result['title']
    ext = info_result['ext']
    filename = f"{platform}_{sanitize_filename(title)}.{ext}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    if os.path.exists(filepath):
        return {
            "status": "success",
            "platform": platform,
            "title": title,
            "filename": filename,
            "download_url": f"{request.base_url}file/{filename}",
            "message": "Bereits heruntergeladen (aus Cache)"
        }

    download_result = await loop.run_in_executor(executor, download_video, url, platform, filepath)

    if not download_result['success']:
        return {"status": "error", "message": f"Fehler beim Download: {download_result['error'][:100]}"}

    if not os.path.exists(filepath):
        return {"status": "error", "message": "Datei konnte nicht erstellt werden"}

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
        "exists": os.path.exists(DOWNLOAD_DIR),
        "yt_dlp_version": yt_dlp.version.__version__
    }