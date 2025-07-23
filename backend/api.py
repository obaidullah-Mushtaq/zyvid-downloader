from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später ggf. Frontend-Domain eintragen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pfad zum Download-Ordner
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Hilfsfunktion: Dateinamen säubern
def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-_. ]", "", name)  # nur erlaubte Zeichen
    return name.replace(" ", "_")

@app.get("/download")
def download_video(
    url: str = Query(..., description="Video-URL"),
    platform: str = Query("youtube", description="Plattform (youtube, tiktok, insta, snapchat)")
):
    try:
        # Zuerst Metadaten holen (ohne Download)
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title", "video")
        ext = info.get("ext", "mp4")
        safe_title = sanitize_filename(title)
        filename = f"{platform}_{safe_title}.{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # Download-Einstellungen
        ydl_opts = {
            'outtmpl': filepath,
            'format': 'best[ext=mp4]/best',
            'quiet': True
        }

        if platform in ["tiktok", "insta", "snapchat"]:
            ydl_opts["format"] = "mp4"

        # Video herunterladen
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return {
            "status": "success",
            "platform": platform,
            "title": title,
            "filename": filename,
            "download_url": f"http://127.0.0.1:8000/file/{filename}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/file/{filename}")
def serve_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    return {"status": "error", "message": "Datei nicht gefunden"}
