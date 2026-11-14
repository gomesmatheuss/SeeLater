from urllib.parse import urlparse, parse_qs


MEDIA_TYPES = [
    ("youtube_video", "YouTube Video"),
    ("youtube_shorts", "YouTube Shorts"),
    ("youtube_channel", "YouTube Channel"),
    ("video", "Vídeo"),
    ("image", "Imagem"),
    ("article", "Artigo"),
    ("website", "Website"),
]


def detect_media_type(url):
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower().split(":")[0]
        path = parsed.path.lower()

        youtube_domains = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
            "youtu.be"
        }

        if hostname in youtube_domains:
            if path.startswith("/shorts/"):
                return "youtube_shorts"

            if hostname == "youtu.be":
                return "youtube_video"

            if path.startswith("/watch"):
                return "youtube_video"

            if (
                path.startswith("/@")
                or path.startswith("/channel/")
                or path.startswith("/c/")
                or path.startswith("/user/")
            ):
                return "youtube_channel"

        return "website"

    except Exception:
        return "website"


def extract_media_id(url, media_type):
    if media_type not in ("youtube_video", "youtube_shorts"):
        return None

    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower().split(":")[0]

        if hostname == "youtu.be":
            return parsed.path.strip("/").split("/")[0] or None

        query = parse_qs(parsed.query)

        if query.get("v"):
            return query["v"][0]

        path_parts = [
            part for part in parsed.path.split("/")
            if part
        ]

        if len(path_parts) >= 2 and path_parts[0] == "shorts":
            return path_parts[1]

    except Exception:
        pass

    return None
