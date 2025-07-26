import requests
import re
import os

def download_instagram_post(url: str, save_path: str) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}"}

        # Direktlink aus HTML extrahieren
        match = re.search(r'"video_url":"([^"]+)"', response.text)
        if not match:
            return {"success": False, "error": "Kein Video gefunden (Reel evtl. privat oder Login nötig)"}

        video_url = match.group(1).replace("\\u0026", "&").replace("\\", "")
        video_data = requests.get(video_url, headers=headers).content

        filename = "instagram_reel.mp4"
        filepath = os.path.join(save_path, filename)

        with open(filepath, "wb") as f:
            f.write(video_data)

        return {"success": True, "filename": filepath}
    except Exception as e:
        return {"success": False, "error": str(e)}
