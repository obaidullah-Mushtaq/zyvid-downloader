import yt_dlp

def download_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # speichert im 'downloads/' Ordner
        'format': 'best[ext=mp4]/best',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print("Fertig heruntergeladen:", info['title'])

if __name__ == "__main__":
    video_url = input("🔗 Gib den Video-Link ein: ")
    download_video(video_url)
