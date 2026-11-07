import flet as ft

from components.group_items.media_cards.youtube_video_card import (
    YouTubeVideoCard
)


class GroupItemCard(ft.Container):

    def __init__(self, item: dict, page: ft.Page, tags=None):
        super().__init__()

        self.item = item
        self.page = page

        media_type = item.get("media_type", "youtube_video")

        card_types = {
            "youtube_video": YouTubeVideoCard
        }

        card_class = card_types.get(media_type)

        if card_class:
            self.content = card_class(
                item=item,
                page=page,
                tags=tags
            )
        else:
            self.content = ft.Container(
                width=280,
                padding=15,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=8,
                content=ft.Text(
                    f"Formato não suportado: {media_type}",
                    color=ft.Colors.GREY_400
                )
            )
