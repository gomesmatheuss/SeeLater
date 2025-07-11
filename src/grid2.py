import flet as ft
import subprocess
import json
import os
import hashlib
import urllib.request

class Card(ft.Container):
    def __init__(self, img_path, title, channel, views):
        super().__init__()
        self.img_path = img_path
        self.title = title
        self.channel = channel
        self.views = views
        self.col = {"xs": 12, "sm": 6, "md": 4, "lg": 3}
        self.padding = 10
        self.content = ft.Column([
            ft.Image(
                src=self.img_path,
                width=320,
                height=180,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(8)
            ),
            ft.Row([
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=20,
                    margin=ft.margin.only(top=10)
                ),
                ft.Container(
                    padding=ft.padding.only(left=10, top=10),
                    expand=True,
                    content=ft.Column([
                        ft.Text(
                            self.title,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Text(
                            self.channel,
                            size=12,
                            color=ft.Colors.GREY_400
                        ),
                        ft.Text(
                            self.views,
                            size=11,
                            color=ft.Colors.GREY_500
                        )
                    ])
                )
            ])
        ])


class Grid(ft.ResponsiveRow):
    def __init__(self):
        super().__init__()
        self.spacing = 10
        self.run_spacing = 20
        self.CACHE_DIR = "./storage/data"
        self.create_cards()

    def hash_video_url(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def get_video_info(self, video_url):
        cache_key = self.hash_video_url(video_url)
        cache_file = os.path.join(self.CACHE_DIR, f"{cache_key}.json")

        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

        try:
            result = subprocess.run(
                ["yt-dlp", "-j", "--no-playlist", video_url],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            print("\n---------\n", json.dumps(data), "\n------\n")
            thumb_url = data.get("thumbnail")
            thumb_path = os.path.join(self.CACHE_DIR, f"{cache_key}.jpg")
            urllib.request.urlretrieve(thumb_url, thumb_path)

            info = {
                "title": data.get("title"),
                "uploader": data.get("uploader"),
                "view_count": data.get("view_count"),
                "thumbnail": thumb_path,
                "webpage_url": data.get("webpage_url")
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

            return info
        except Exception as e:
            print("Erro ao obter info do vídeo:", e)
            return None
    
    def build_video_card(self, video_url):
        info = self.get_video_info(video_url)
        if not info:
            return Card(
                os.path.join(self.CACHE_DIR, "img_teste.jpg"),
                "Vídeo Não Encontrado",
                "",
                ""
            )
        
        return Card(
            info["thumbnail"],
            info["title"],
            info["uploader"],
            f"{info['view_count']:,} visualizações"
        )
    
    def create_cards(self):
        with open(os.path.join(self.CACHE_DIR, "videos.json"), "r", encoding="utf-8") as f:
            VIDEO_LINKS = json.loads(f.read())

        for url in VIDEO_LINKS:
            self.controls.append(self.build_video_card(f"https://www.youtube.com/watch?v={url.get('id')}"))
