import flet as ft
from models.video import Video

class Card(ft.Container):
    def __init__(self, video: Video):
        super().__init__()
        self.padding = 2
        self.width = 280
        self.content = ft.Column([
            ft.Image(
                src=video.thumbnail_path,
                width=320,
                height=180,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(8),
                aspect_ratio=1280/720
            ),
            ft.Row([
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=20,
                    margin=ft.margin.only(top=2)
                ),
                ft.Container(
                    padding=ft.padding.only(left=10, top=10),
                    expand=True,
                    content=ft.Column([
                        ft.Text(
                            video.title,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Text(
                            video.uploader,
                            size=12,
                            color=ft.Colors.GREY_400
                        ),
                        ft.Text(
                            f"{video.view_count:,} visualizações",
                            size=11,
                            color=ft.Colors.GREY_500
                        )
                    ])
                )
            ])
        ])
