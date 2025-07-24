from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import re
import logging
import os
import json
from pathlib import Path
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
        'extract_flat': False,
        'retries': 3,
    }
    
    if platform == "youtube":
        return {
            **base_opts,
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    elif platform == "tiktok":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
        }
    elif platform == "instagram":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
        }
    elif platform == "snapchat":
        return {
            **base_opts,
            'format': 'best[ext=mp4]/best',
        }
    
    return base_opts

@app.get("/")
async def root():
    return {"status": "active", "message": "Video Downloader API läuft"}

@app.get("/download")
async def download_video(
    request: Request,
    url: str = Query(...),
    platform: str = Query("youtube")
):
    logger.info(f"Download-Request: URL={url}, Platform={platform}")
    
    try:
        if not url or not url.startswith(('http://', 'https://')):
            return {"status": "error", "message": "Ungültige URL"}
        
        ydl_opts = get_platform_options(platform)
        
        # Video-Informationen extrahieren
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info(f"Video-Info extrahiert: {info.get('title', 'Unbekannt')}")
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren: {str(e)}")
            
            # Plattform-spezifische Fehlermeldungen
            if platform == "youtube" and ("bot" in str(e).lower() or "sign in" in str(e).lower()):
                return {"status": "error", "message": "YouTube hat Bot-Detection aktiviert. Derzeit nicht verfügbar."}
            elif platform == "instagram" and ("login" in str(e).lower() or "rate" in str(e).lower()):
                return {"status": "error", "message": "Instagram verlangt Anmeldung oder Rate-Limit erreicht."}
            elif platform == "snapchat":
                return {"status": "error", "message": "Snapchat-Links sind oft nur temporär verfügbar."}
            else:
                return {"status": "error", "message": f"Fehler beim Laden des Videos: {str(e)}"}

        # Dateiname generieren
        title = info.get("title", "video")
        ext = info.get("ext", "mp4")
        safe_title = sanitize_filename(title)
        filename = f"{platform}_{safe_title}.{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # Download-Optionen
        download_opts = {
            **ydl_opts,
            'outtmpl': filepath,
        }

        # Video herunterladen
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])
            logger.info(f"Download abgeschlossen: {filename}")

        # Prüfen ob Datei existiert
        if not os.path.exists(filepath):
            return {"status": "error", "message": "Download fehlgeschlagen - Datei nicht gefunden"}

        return {
            "status": "success",
            "platform": platform,
            "title": title,
            "filename": filename,
            "download_url": f"{request.base_url}file/{filename}",
            "message": "Video erfolgreich heruntergeladen"
        }

    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}")
        return {"status": "error", "message": f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"}

@app.get("/file/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    
    if os.path.exists(file_path):
        logger.info(f"Datei wird ausgeliefert: {filename}")
        return FileResponse(
            file_path, 
            media_type="video/mp4", 
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        logger.warning(f"Datei nicht gefunden: {filename}")
        return {"status": "error", "message": "Datei nicht gefunden"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "downloads_dir": DOWNLOAD_DIR,
        "downloads_dir_exists": os.path.exists(DOWNLOAD_DIR)
    }