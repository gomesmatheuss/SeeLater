import flet as ft
from services.utils import format_timestamp
from models.video import Video
from components.edit_video_alertdialog import EditVideo


class CardTexts(ft.Column):

    def __init__(self, video: Video):
        super().__init__()

        self.video = video

        self.spacing = 0
        self.expand = 1

        self.controls = [
            ft.Row(
                expand=1,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(
                            top=-3,
                            bottom=2
                        ),
                        expand=1,
                        on_click=self.copy_url_to_clipboard,
                        content=ft.Text(
                            value=video.title,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=13,
                            font_family="Roboto",
                            style=ft.TextStyle(height=1.2),
                            weight=ft.FontWeight.BOLD,
                            tooltip=ft.Tooltip(
                                video.title,
                                wait_duration=ft.Duration(
                                    milliseconds=600
                                )
                            )
                        )
                    )
                ]
            ),

            ft.Row(
                height=16,
                expand=1,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(top=-4),
                        expand=1,
                        content=ft.Text(
                            value=video.uploader,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=12,
                            font_family="Roboto",
                            color=ft.Colors.GREY_400,
                            tooltip=ft.Tooltip(
                                video.uploader,
                                wait_duration=ft.Duration(
                                    milliseconds=600
                                )
                            )
                        )
                    )
                ]
            ),

            ft.Row(
                height=16,
                expand=1,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(top=-6),
                        expand=1,
                        content=ft.Text(
                            f"{video.view_count:,} visualizações - "
                            f"{format_timestamp(video.upload_date)}",
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=11,
                            font_family="Roboto",
                            color=ft.Colors.GREY_500
                        )
                    )
                ]
            )
        ]

    def copy_url_to_clipboard(self, e):
        e.control.page.set_clipboard(
            self.video.url
        )

        e.control.page.open(
            ft.SnackBar(
                ft.Text(
                    f"Copied to clipboard: {self.video.url}"
                ),
                open=True
            )
        )


class Card(ft.Column):

    def __init__(
        self,
        video: Video,
        page: ft.Page,
        on_changed=None
    ):
        super().__init__()

        self.video = video
        self.page = page
        self.on_changed = on_changed

        self.width = 280
        self.alignment = ft.MainAxisAlignment.START

        self.controls = [
            ft.Row(
                [
                    ft.Container(
                        expand=1,
                        content=ft.Image(
                            src=video.thumbnail_path,
                            width=320,
                            height=180,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(8),
                            aspect_ratio=1280 / 720,
                            expand=True
                        ),
                        on_click=self.open_edit_video_dialog
                    )
                ]
            ),

            ft.Row(
                [
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=ft.Colors.GREY_700,
                        border_radius=20,
                        margin=ft.margin.only(top=2)
                    ),

                    CardTexts(video),

                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.PopupMenuButton(
                                padding=1,
                                menu_padding=1,
                                width=25,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Marcar Como Visto",
                                        height=30,
                                        on_click=self.watched_click
                                    ),

                                    ft.PopupMenuItem(
                                        text="Mover Para o Topo",
                                        height=30
                                    ),

                                    ft.PopupMenuItem(
                                        text="Mover Para Último",
                                        height=30
                                    ),

                                    ft.PopupMenuItem(
                                        text="Carregar Informações",
                                        height=30
                                    ),

                                    ft.PopupMenuItem(
                                        text="Ocultar",
                                        height=30
                                    ),

                                    ft.PopupMenuItem(
                                        text="Excluir",
                                        height=30
                                    )
                                ]
                            )
                        ]
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ]

    def open_edit_video_dialog(self, e):
        dlg = EditVideo(self.video)

        self.page.overlay.append(dlg)

        dlg.open = True

        self.page.update()

    def watched_click(self, e):
        self.page.open(
            ft.SnackBar(
                ft.Text(
                    f"Marked as viewed: {self.video.title}"
                ),
                open=True
            )
        )

        if self.on_changed:
            self.on_changed(self.video)

