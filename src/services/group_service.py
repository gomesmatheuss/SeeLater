
from services.db_service import (
    get_all_groups,
    get_group_by_id,
    get_group_items,
    get_all_tags
)


class GroupService:

    def __init__(self):
        self.groups_cache = None
        self.items_cache = {}
        self.tags_by_name = {}
        self.tags_loaded = False

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
    # ITENS DOS GRUPOS
    # --------------------------------------------------

    def get_group_items(self, group_id, hard_refresh=False):
        """
        Retorna os documentos independentes de um grupo.

        Não consulta as coleções globais de vídeos ou Tabs.
        """

        group_id = str(group_id)

        if group_id not in self.items_cache or hard_refresh:
            group = self.get_group(group_id, hard_refresh)

            if not group:
                return []

            self.items_cache[group_id] = get_group_items(group_id)

        return self.items_cache[group_id]

    def get_group_preview(self, group_id, limit=4):
        """
        Retorna os primeiros itens do grupo para sua prévia.
        """

        return self.get_group_items(group_id)[:limit]

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

        As tags pertencem ao próprio documento do item,
        não mais à Tab global.
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
        self.tags_by_name.clear()
        self.tags_loaded = False
