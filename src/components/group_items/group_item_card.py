
import flet as ft

from components.group_items.media_cards.youtube_video_card import (
    YouTubeVideoCard
)

from components.group_items.media_cards.generic_media_card import (
    GenericMediaCard
)


class GroupItemCard(ft.Container):

    def __init__(self, item: dict, page: ft.Page, tags=None):
        super().__init__()

        self.item = item
        self.page = page

        media_type = item.get("media_type", "website")

        card_types = {
            "youtube_video": YouTubeVideoCard,
            "youtube_shorts": YouTubeVideoCard,
        }

        card_class = card_types.get(
            media_type,
            GenericMediaCard
        )

        self.content = card_class(
            item=item,
            page=page,
            tags=tags
        )
