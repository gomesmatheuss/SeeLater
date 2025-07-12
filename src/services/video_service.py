import subprocess
import json
import os
import urllib.request
from services.utils import hash_video_url
from models.video import Video

CACHE_DIR = "./storage/data"

def get_video_info(video_url):
    cache_key = hash_video_url(video_url)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Video(
                id=cache_key,
                title=data["title"],
                uploader=data["uploader"],
                view_count=data["view_count"],
                thumbnail_path=data["thumbnail"]
            )

    try:
        result = subprocess.run(
            ["yt-dlp", "-j", "--no-playlist", video_url],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        thumb_url = data.get("thumbnail")
        thumb_path = os.path.join(CACHE_DIR, f"{cache_key}.jpg")
        urllib.request.urlretrieve(thumb_url, thumb_path)

        info = {
            "title": data.get("title"),
            "uploader": data.get("uploader"),
            "view_count": data.get("view_count"),
            "thumbnail": thumb_path
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        return Video(
            id=cache_key,
            title=info["title"],
            uploader=info["uploader"],
            view_count=info["view_count"],
            thumbnail_path=info["thumbnail"]
        )
    except Exception as e:
        print("Erro ao obter info do vídeo:", e)
        return None
