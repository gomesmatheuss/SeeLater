import flet as ft
from services.video_service import get_video_info
from services.db_service import get_tabs_list, get_all_videos
from components.video_card import Card

class Grid(ft.ResponsiveRow):
    def __init__(self):
        super().__init__()
        self.spacing = 10
        self.run_spacing = 20
        self.create_cards()

    def create_cards(self):
        # videos_links = get_all_videos()

        # for url in videos_links:
        #     full_url = f"https://www.youtube.com/watch?v={url.get('id')}"
        #     video = get_video_info(full_url)
        #     if video:
        #         self.controls.append(Card(video))

        tabs = get_tabs_list()

        for tab in tabs:
            if "youtube" in tab["url"]:
                video = get_video_info(tab["url"])
                if video:
                    self.controls.append(Card(video))