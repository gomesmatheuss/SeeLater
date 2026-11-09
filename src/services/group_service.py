
from services.db_service import (
    get_all_groups,
    get_group_by_id,
    get_group_items,
    get_all_tags,
    get_all_videos
)
from services.video_service import ensure_video_thumbnail

from models.enums.load_status import LoadStatus
from models.video import Video


class GroupService:

    def __init__(self):
        self.groups_cache = None
        self.items_cache = {}
        self.videos_cache = None

        self.tags_by_name = {}
        self.tags_loaded = False

        self.checked_video_thumbnails = set()

    # --------------------------------------------------
    # GRUPOS
    # --------------------------------------------------

    def load_groups(self, hard_refresh=False):

        if self.groups_cache is None or hard_refresh:
            self.groups_cache = get_all_groups()

        return self.groups_cache

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

    # --------------------------------------------------
    # VÍDEOS
    # --------------------------------------------------

    def load_videos(self, hard_refresh=False):
        """
        Carrega os metadados compartilhados dos vídeos.
        """

        if self.videos_cache is None or hard_refresh:
            self.videos_cache = get_all_videos()

        return self.videos_cache

    # --------------------------------------------------
    # ITENS DOS GRUPOS
    # --------------------------------------------------

    def get_group_items(self, group_id, hard_refresh=False):
        """
        Retorna os documentos independentes de um grupo,
        combinados com os metadados globais dos vídeos.

        Os dados próprios do grupo têm prioridade sobre
        os dados da coleção global.
        """

        group_id = str(group_id)

        if group_id not in self.items_cache or hard_refresh:

            group = self.get_group(
                group_id,
                hard_refresh
            )

            if not group:
                return []

            items = get_group_items(group_id)

            videos = self.load_videos(
                hard_refresh=hard_refresh
            )

            enriched_items = []

            for item in items:

                media_id = item.get("media_id")
                video_data = videos.get(media_id, {})

                enriched_item = {**video_data, **item}

                # Recupera informações do vídeo quando o item do grupo
                # ainda não possui esses dados.
                fields_to_inherit = [
                    "thumbnail_path",
                    "title",
                    "uploader",
                    "view_count",
                    "upload_date",
                    "duration",
                    "channel_id",
                    "channel_thumbnail_path"
                ]

                for field in fields_to_inherit:

                    if not enriched_item.get(field):
                        enriched_item[field] = video_data.get(field)

                enriched_items.append(enriched_item)

            self.items_cache[group_id] = enriched_items

        # Verifica se as thumbnails dos vídeos continuam disponíveis.
        # Essa verificação também acontece quando os itens vêm do cache.
        for item in self.items_cache[group_id]:

            if item.get("media_type") not in (
                "youtube_video",
                "youtube_shorts"
            ):
                continue

            media_id = item.get("media_id")

            if not media_id:
                continue

            # Não verifica novamente vídeos já processados.
            if media_id in self.checked_video_thumbnails:
                continue

            video_data = self.videos_cache.get(media_id)

            if not video_data:
                continue

            video = Video.from_dict(video_data)

            video = ensure_video_thumbnail(video)

            item["thumbnail_path"] = video.thumbnail_path

            self.checked_video_thumbnails.add(media_id)

        return self.items_cache[group_id]

    def get_group_preview(self, group_id, limit=4):
        """
        Retorna os primeiros itens do grupo para sua prévia.
        """

        return self.get_group_items(group_id)[:limit]

    def get_pending_items(self, items):
        """
        Retorna somente os vídeos que ainda aguardam
        o primeiro carregamento de metadados.
        """

        pending_statuses = {
            LoadStatus.JSON_IMPORTED,
            LoadStatus.READY_FOR_LOAD
        }

        pending_items = []

        for item in items:

            # Por enquanto, a fila processa vídeos do YouTube.
            if item.get("media_type") != "youtube_video":
                continue

            status = item.get(
                "load_status",
                LoadStatus.LOAD_FAILED
            )

            if type(status) == int:
                status = LoadStatus.LOAD_FAILED

            try:

                if not isinstance(status, LoadStatus):
                    status = LoadStatus(status)

            except (ValueError, TypeError):
                continue

            if status in pending_statuses:
                pending_items.append(item)

        return pending_items

    # --------------------------------------------------
    # TAGS
    # --------------------------------------------------

    def load_tags(self, hard_refresh=False):
        """
        Carrega as tags cadastradas e suas cores.
        """

        if not self.tags_loaded or hard_refresh:

            tags = get_all_tags()

            self.tags_by_name = {
                tag["name"]: tag
                for tag in tags
            }

            self.tags_loaded = True

    def get_item_tags(self, item, hard_refresh=False):
        """
        Retorna as tags de um item com suas respectivas cores.
        """

        self.load_tags(hard_refresh)

        if isinstance(item, dict):
            tag_names = item.get("tags", [])
        else:
            tag_names = []

        return [
            {
                "name": tag_name,
                "color": self.tags_by_name.get(
                    tag_name, {}
                ).get("color", "#2196F3")
            }
            for tag_name in tag_names
        ]

    # Compatibilidade temporária com chamadas antigas.
    def get_video_tags(self, item):
        return self.get_item_tags(item)

    # --------------------------------------------------
    # CACHE
    # --------------------------------------------------

    def invalidate_cache(self):

        self.groups_cache = None
        self.items_cache.clear()
        self.videos_cache = None

        self.tags_by_name.clear()
        self.tags_loaded = False
