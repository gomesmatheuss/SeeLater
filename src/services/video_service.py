import subprocess
import json
import os
import urllib.request
import pathlib
import re
from datetime import datetime
from services.utils import get_yt_url_code
from models.video import Video
from models.tab import Tab
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType
from services.db_service import save_video, save_tab, get_video_by_id

CACHE_DIR = "./storage/data/videos_thumb"
pathlib.Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def get_video_info(tab: dict):
    cache_key = get_yt_url_code(tab.get("url", ""))

    if not cache_key or "youtube" not in tab.get("url", ""):
        return get_not_loaded_video_info(tab)

    if (existing := get_video_by_id(cache_key)) and existing.get("load_status") == LoadStatus.LOAD_SUCCESS:
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
        thumb_url = re.sub(r"(hqdefault|maxresdefault|sddefault)", "mqdefault", data.get("thumbnail"))
        thumb_path = os.path.join(CACHE_DIR, f"{cache_key}.jpg")
        urllib.request.urlretrieve(thumb_url, thumb_path)

        return Video(
            id = cache_key,
            url = tab["url"],
            title = data.get("title"),
            uploader = data.get("uploader"),
            view_count = data.get("view_count"),
            thumbnail_path = thumb_path,
            upload_date = data.get("timestamp"),
            duration = data.get("duration_string"),
            channel_id = data.get("channel_id"),
            last_update = datetime.now(),
            load_status = LoadStatus.LOAD_SUCCESS,
            media_type = MediaType.YOUTUBE_VIDEO,
            active = True
        )
    
    except Exception as e:
        print("Erro ao obter info do vídeo:", e)
        return None
    
def get_not_loaded_video_info(tab: dict):
    cache_key = get_yt_url_code(tab.get("url", ""))

    return Video(
        id = cache_key,
        url = tab.get("url"),
        title = tab.get("title"),
        uploader = "?",
        view_count = 0,
        thumbnail_path = os.path.join(CACHE_DIR, "image-not-found.png"),
        upload_date = datetime.now(),
        duration = "00:00",
        channel_id = "",
        last_update = datetime.now(),
        load_status = LoadStatus.LOAD_FAILED,
        media_type = MediaType.YOUTUBE_VIDEO if "youtube" in tab.get("url") else MediaType.OTHER_SITE,
        active = True
    )

def save_from_url(tab: Tab):
    video = get_video_info(tab.to_dict())
    if not video:
        video = get_not_loaded_video_info(tab.to_dict())

    tab.title = video.title
    tab.load_status = video.load_status
    tab.content_id = video.id
    tab.media_type = video.media_type
    tab.last_update = datetime.now()

    save_video(video.to_dict())
    save_tab(tab)

def load_card_info(tab: dict, VIDEOS):
    if "youtube" in tab["url"]:
        #usando isso enquanto não corrijo o banco
        tab["load_status"] = LoadStatus.LOAD_FAILED if type(tab.get("load_status")) == int else tab["load_status"]

        if LoadStatus(tab.get("load_status", LoadStatus.LOAD_FAILED)) == LoadStatus.LOAD_SUCCESS:
            yt_id = get_yt_url_code(tab.get("url"))
            return Video.from_dict(VIDEOS.get(yt_id))

        return get_not_loaded_video_info(tab)
