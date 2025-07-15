import subprocess
import json
import os
import urllib.request
import pathlib
from services.utils import get_yt_url_code
from models.video import Video
from services.db_service import save_video, get_video_by_id

CACHE_DIR = "./storage/data/videos_thumb"
pathlib.Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def get_video_info(video_url):
    cache_key = get_yt_url_code(video_url)

    existing = get_video_by_id(cache_key)
    if existing:
        return Video.from_dict(existing)

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

def load_all_videos_from_db():
    from services.db_service import get_all_videos
    docs = get_all_videos()
    return [Video.from_dict(doc) for doc in docs]
