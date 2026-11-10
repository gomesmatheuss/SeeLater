
from components.media_cards.youtube_video_card import YouTubeVideoCard
from components.media_cards.generic_media_card import GenericMediaCard


class MediaCardAssembler:

    @staticmethod
    def create_card(item, page, tags=None):

        if isinstance(item, dict):
            item_data = item.copy()
        else:
            item_data = item.__dict__.copy()

        media_type = item_data.get("media_type", "website")

        # Converte enums para seus valores em string.
        media_type = getattr(media_type, "value", media_type)

        # Mantém o formato padronizado para os cards.
        item_data["media_type"] = media_type

        card_types = {
            "youtube_video": YouTubeVideoCard,
            "youtube_shorts": YouTubeVideoCard,
        }

        card_class = card_types.get(media_type, GenericMediaCard)

        return card_class(
            item=item_data,
            page=page,
            tags=tags
        )
