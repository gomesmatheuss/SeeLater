import flet as ft
from services.utils import format_timestamp
from models.video import Video

class CardTexts(ft.Column):
    def __init__(self, video: Video):
        super().__init__()
        self.spacing = 0
        self.expand = 1
        self.controls = [
            ft.Row(
                expand = 1,
                controls = [
                    ft.Container(
                        padding = ft.padding.only(top=-3, bottom=2),
                        expand = 1,
                        content = ft.Text(
                            value = video.title,
                            max_lines = 2,
                            overflow = ft.TextOverflow.ELLIPSIS,
                            size = 13,
                            font_family = "Roboto",
                            style = ft.TextStyle(height=1.2),
                            weight = ft.FontWeight.BOLD
                        )
                    )
                ]
            ),
            ft.Row(
                height = 16,
                expand = 1,
                controls = [
                    ft.Container(
                        padding = ft.padding.only(top=-4),
                        expand = 1,
                        content = ft.Text(
                            value = video.uploader,
                            max_lines = 1,
                            overflow = ft.TextOverflow.ELLIPSIS,
                            size = 12,
                            font_family = "Roboto",
                            color=ft.Colors.GREY_400
                        )
                    )
                ]
            ),
            ft.Row(
                height = 16,
                expand = 1,
                controls = [
                    ft.Container(
                        padding = ft.padding.only(top=-6),
                        expand = 1,
                        content = ft.Text(
                            f"{video.view_count:,} visualizações - {format_timestamp(video.upload_date)}",
                            max_lines = 1,
                            overflow = ft.TextOverflow.ELLIPSIS,
                            size = 11,
                            font_family = "Roboto",
                            color=ft.Colors.GREY_500
                        )
                    )
                ]
            )
        ]


class Card(ft.Column):
    def __init__(self, video: Video):
        super().__init__()
        self.width = 280
        self.alignment = ft.MainAxisAlignment.START
        self.controls = [
            ft.Row([
                ft.Image(
                    src=video.thumbnail_path,
                    width=320,
                    height=180,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8),
                    aspect_ratio=1280/720,
                    expand=True
                )
            ]),
            ft.Row([
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=20,
                    margin=ft.margin.only(top=2)
                ),
                CardTexts(video)
            ],
            vertical_alignment=ft.CrossAxisAlignment.START)
        ]
