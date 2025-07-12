import flet as ft
import json
import os
from services.video_service import get_video_info
from video_card import Card

class Grid(ft.ResponsiveRow):
    def __init__(self):
        super().__init__()
        self.spacing = 10
        self.run_spacing = 20
        self.CACHE_DIR = "./storage/data"
        self.create_cards()

    def create_cards(self):
        with open(os.path.join(self.CACHE_DIR, "videos.json"), "r", encoding="utf-8") as f:
            video_links = json.load(f)

        for url in video_links:
            full_url = f"https://www.youtube.com/watch?v={url.get('id')}"
            video = get_video_info(full_url)
            if video:
                self.controls.append(Card(video))
