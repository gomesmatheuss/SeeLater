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
CHANNEL_CACHE_DIR = "./storage/data/channels_thumb"

pathlib.Path(CACHE_DIR).mkdir(
    parents=True,
    exist_ok=True
)

pathlib.Path(CHANNEL_CACHE_DIR).mkdir(
    parents=True,
    exist_ok=True
)


def get_channel_thumbnail(channel_url, channel_id):
    """
    Obtém e armazena a imagem do canal.

    O arquivo é salvo usando o channel_id como nome.

    Quando o avatar não pode ser obtido, é criado um arquivo
    .failed para impedir novas tentativas automáticas nas
    próximas execuções do programa.
    """

    if not channel_id:
        return None

    channel_path = os.path.join(
        CHANNEL_CACHE_DIR,
        f"{channel_id}.jpg"
    )

    failed_path = os.path.join(
        CHANNEL_CACHE_DIR,
        f"{channel_id}.failed"
    )

    # Avatar já existe.
    if os.path.exists(channel_path):
        return channel_path

    # Já tentamos anteriormente e não conseguimos.
    if os.path.exists(failed_path):
        return None

    if not channel_url:
        pathlib.Path(failed_path).touch()

        return None

    try:
        print(
            "buscando avatar do canal -",
            channel_id
        )

        result = subprocess.run(
            [
                "yt-dlp",
                "--playlist-items", "0",
                "-J",
                channel_url
            ],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout.strip()

        if not output:
            print(
                "yt-dlp não retornou dados para o canal:",
                channel_id
            )

            pathlib.Path(failed_path).touch()

            if result.stderr:
                print(
                    "yt-dlp:",
                    result.stderr.strip()
                )

            return None

        data = json.loads(output)

        thumbnails = data.get(
            "thumbnails",
            []
        )

        avatar_url = None

        # Preferimos avatar_uncropped.
        for thumbnail in thumbnails:
            if thumbnail.get("id") == "avatar_uncropped":
                avatar_url = thumbnail.get("url")
                break

        # Fallback para qualquer thumbnail de avatar.
        if not avatar_url:
            for thumbnail in thumbnails:
                thumbnail_id = str(
                    thumbnail.get("id", "")
                ).lower()

                if "avatar" in thumbnail_id:
                    avatar_url = thumbnail.get("url")
                    break

        if not avatar_url:
            print(
                "Avatar não encontrado para o canal:",
                channel_id
            )

            pathlib.Path(failed_path).touch()

            return None

        urllib.request.urlretrieve(
            avatar_url,
            channel_path
        )

        print(
            "Avatar salvo:",
            channel_path
        )

        return channel_path

    except json.JSONDecodeError as e:
        print(
            "yt-dlp não retornou JSON válido para o canal:",
            channel_id
        )

        pathlib.Path(failed_path).touch()

        if result.stdout:
            print(
                "stdout:",
                result.stdout[:500]
            )

        if result.stderr:
            print(
                "stderr:",
                result.stderr[:500]
            )

        return None

    except Exception as e:
        print(
            "Erro ao obter avatar do canal:",
            channel_id,
            e
        )

        pathlib.Path(failed_path).touch()

        return None


def get_video_info(tab: dict):
    cache_key = get_yt_url_code(
        tab.get("url", "")
    )

    if not cache_key or "youtube" not in tab.get("url", ""):
        return get_not_loaded_video_info(tab)

    if (
        existing := get_video_by_id(cache_key)
    ) and existing.get("load_status") == LoadStatus.LOAD_SUCCESS:
        return Video.from_dict(existing)

    try:
        print(
            "buscando da net -",
            cache_key,
            "-",
            tab.get("title")
        )

        result = subprocess.run(
            [
                "yt-dlp",
                "-j",
                "--no-playlist",
                tab.get("url")
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        thumb_url = re.sub(
            r"(hqdefault|maxresdefault|sddefault)",
            "mqdefault",
            data.get("thumbnail")
        )

        thumb_path = os.path.join(
            CACHE_DIR,
            f"{cache_key}.jpg"
        )

        # Não baixa novamente a thumbnail se ela já existir.
        if not os.path.exists(thumb_path):
            urllib.request.urlretrieve(
                thumb_url,
                thumb_path
            )

        channel_id = data.get("channel_id")
        channel_url = data.get("channel_url")

        channel_thumbnail_path = get_channel_thumbnail(
            channel_url,
            channel_id
        )

        return Video(
            id=cache_key,
            url=tab["url"],
            title=data.get("title"),
            uploader=data.get("uploader"),
            view_count=data.get("view_count"),
            thumbnail_path=thumb_path,
            upload_date=data.get("timestamp"),
            duration=data.get("duration_string"),
            channel_id=channel_id,
            channel_thumbnail_path=channel_thumbnail_path,
            last_update=datetime.now(),
            load_status=LoadStatus.LOAD_SUCCESS,
            media_type=MediaType.YOUTUBE_VIDEO,
            active=True
        )

    except Exception as e:
        print(
            "Erro ao obter info do vídeo:",
            e
        )

        return None


def get_not_loaded_video_info(tab: dict):
    cache_key = get_yt_url_code(
        tab.get("url", "")
    )

    return Video(
        id=cache_key,
        url=tab.get("url"),
        title=tab.get("title"),
        uploader="?",
        view_count=0,
        thumbnail_path=os.path.join(
            CACHE_DIR,
            "image-not-found.png"
        ),
        upload_date=datetime.now(),
        duration="00:00",
        channel_id="",
        channel_thumbnail_path=None,
        last_update=datetime.now(),
        load_status=LoadStatus.LOAD_FAILED,
        media_type=(
            MediaType.YOUTUBE_VIDEO
            if "youtube" in tab.get("url")
            else MediaType.OTHER_SITE
        ),
        active=True
    )


def ensure_channel_thumbnail(video: Video):
    """
    Garante que o Video tenha um avatar de canal disponível.

    É especialmente útil para vídeos antigos que já estavam
    salvos no banco antes da implementação do cache de canais.
    """

    if not video.channel_id:
        return video

    # O caminho determinístico permite reutilizar o arquivo
    # mesmo que o campo ainda não exista no banco.
    channel_path = os.path.join(
        CHANNEL_CACHE_DIR,
        f"{video.channel_id}.jpg"
    )

    if os.path.exists(channel_path):
        video.channel_thumbnail_path = channel_path
        return video

    # Vídeos antigos podem não ter channel_url armazenada.
    # Nesse caso, montamos a URL usando o channel_id.
    channel_url = (
        f"https://www.youtube.com/channel/"
        f"{video.channel_id}"
    )

    channel_thumbnail_path = get_channel_thumbnail(
        channel_url,
        video.channel_id
    )

    if channel_thumbnail_path:
        video.channel_thumbnail_path = channel_thumbnail_path

    return video


def save_from_url(tab: Tab):
    video = get_video_info(
        tab.to_dict()
    )

    if not video:
        video = get_not_loaded_video_info(
            tab.to_dict()
        )

    tab.title = video.title
    tab.load_status = video.load_status
    tab.content_id = video.id
    tab.media_type = video.media_type
    tab.last_update = datetime.now()

    save_video(
        video.to_dict()
    )

    save_tab(
        tab
    )


def load_card_info(tab: dict, VIDEOS):
    if "youtube" in tab["url"]:

        # usando isso enquanto não corrijo o banco
        tab["load_status"] = (
            LoadStatus.LOAD_FAILED
            if type(tab.get("load_status")) == int
            else tab["load_status"]
        )

        if (
            LoadStatus(
                tab.get(
                    "load_status",
                    LoadStatus.LOAD_FAILED
                )
            )
            == LoadStatus.LOAD_SUCCESS
        ):

            yt_id = get_yt_url_code(
                tab.get("url")
            )

            video_data = VIDEOS.get(yt_id)

            if not video_data:
                return None

            video = Video.from_dict(
                video_data
            )

            # Garante o avatar também para vídeos
            # que já existiam antes dessa implementação.
            video = ensure_channel_thumbnail(
                video
            )

            return video

        return get_not_loaded_video_info(
            tab
        )

    return None
