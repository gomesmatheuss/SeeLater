import subprocess
import json
import os
import urllib.request
import pathlib
from datetime import datetime
from services.utils import get_yt_url_code
from models.video import Video
from services.db_service import save_video, get_video_by_id

CACHE_DIR = "./storage/data/videos_thumb"
pathlib.Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def get_video_info(tab: dict):
    cache_key = get_yt_url_code(tab.get("url", ""))

    if not cache_key:
        return get_not_loaded_video_info(tab)

    existing = get_video_by_id(cache_key)
    if existing:
        return Video.from_dict(existing)

    try:
        print("buscando da net -", cache_key, "-", tab.get("title"))
        
        result = subprocess.run(
            ["yt-dlp", "-j", "--no-playlist", tab.get("url")],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        thumb_url = data.get("thumbnail")
        thumb_path = os.path.join(CACHE_DIR, f"{cache_key}.jpg")
        urllib.request.urlretrieve(thumb_url, thumb_path)

        info = {
            "id": cache_key,
            "title": data.get("title"),
            "uploader": data.get("uploader"),
            "view_count": data.get("view_count"),
            "thumbnail_path": thumb_path,
            "upload_date": data.get("timestamp"),
            "duration": data.get("duration_string"),
            "channel_id": data.get("channel_id"), 
        }
        
        save_video(info)

        return Video.from_dict(info)
    
    except Exception as e:
        print("Erro ao obter info do vídeo:", e)
        return None
    
def get_not_loaded_video_info(tab: dict):
    cache_key = get_yt_url_code(tab.get("url", ""))

    return Video(
        id=cache_key,
        title=tab.get("title"),
        uploader="?",
        view_count=0,
        thumbnail_path=os.path.join(CACHE_DIR, "image-not-found.png"),
        upload_date=datetime.now(),
        duration="00:00",
        channel_id=""
    )

def load_all_videos_from_db():
    from services.db_service import get_all_videos
    docs = get_all_videos()
    return [Video.from_dict(doc) for doc in docs]
