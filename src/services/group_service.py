
from services.db_service import (
    get_all_groups,
    get_group_by_id,
    get_all_videos,
    get_tabs_by_urls,
    get_all_tags
)

from services.video_service import ensure_channel_thumbnail
from models.video import Video


class GroupService:

    def __init__(self):
        self.groups_cache = None
        self.videos_cache = None

        self.tabs_by_url = {}
        self.tags_by_name = {}
        self.metadata_loaded = False

    def load_groups(self, hard_refresh=False):
        if self.groups_cache is None or hard_refresh:
            self.groups_cache = get_all_groups()

        return self.groups_cache

    def load_videos(self, hard_refresh=False):
        if self.videos_cache is None or hard_refresh:
            self.videos_cache = get_all_videos()

        return self.videos_cache

    def load_metadata(self, videos, hard_refresh=False):
        """
        Carrega as informações de Tabs e Tags,
        incluindo vídeos inativos ou marcados como vistos.
        """

        if self.metadata_loaded and not hard_refresh:
            return

        urls = [
            video.get("url")
            for video in videos.values()
            if video.get("url")
        ]

        tabs = get_tabs_by_urls(urls)
        tags = get_all_tags()

        self.tabs_by_url = {
            tab["url"]: tab
            for tab in tabs
        }

        self.tags_by_name = {
            tag["name"]: tag
            for tag in tags
        }

        self.metadata_loaded = True

    def get_groups(self, hard_refresh=False):
        return self.load_groups(hard_refresh)

    def get_group(self, group_id, hard_refresh=False):

        if hard_refresh:
            return get_group_by_id(group_id)

        groups = self.load_groups()

        for group in groups:
            if str(group["_id"]) == str(group_id):
                return group

        group = get_group_by_id(group_id)

        if group:
            self.groups_cache.append(group)

        return group

    def get_group_items(self, group_id, hard_refresh=False):

        group = self.get_group(group_id, hard_refresh)

        if not group:
            return []

        videos = self.load_videos(hard_refresh)

        self.load_metadata(videos, hard_refresh)

        items = []

        for item in group.get("items", []):

            media_type = item.get("media_type")
            media_id = str(item.get("media_id"))

            if media_type != "video":
                continue

            video_data = videos.get(media_id)

            if not video_data:
                continue

            video = Video.from_dict(video_data)
            video = ensure_channel_thumbnail(video)

            items.append(video)

        return items

    def get_video_tags(self, video):
        """
        Retorna as tags associadas ao vídeo,
        incluindo suas respectivas cores.
        """

        tab = self.tabs_by_url.get(video.url)

        if not tab:
            return []

        return [
            {
                "name": tag_name,
                "color": self.tags_by_name[tag_name].get(
                    "color",
                    "#2196F3"
                )
            }
            for tag_name in tab.get("tags", [])
            if tag_name in self.tags_by_name
        ]

    def get_group_preview(self, group_id, limit=4):

        items = self.get_group_items(group_id)

        return items[:limit]

    def invalidate_cache(self):

        self.groups_cache = None
        self.videos_cache = None

        self.tabs_by_url.clear()
        self.tags_by_name.clear()

        self.metadata_loaded = False
