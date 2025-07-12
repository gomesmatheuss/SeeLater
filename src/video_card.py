import flet as ft

class Card(ft.Container):
    def __init__(self, video):
        super().__init__()
        self.col = {"xs": 12, "sm": 6, "md": 4, "lg": 3}
        self.padding = 10
        self.content = ft.Column([
            ft.Image(
                src=video.thumbnail_path,
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
