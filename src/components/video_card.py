import flet as ft

from services.utils import format_timestamp, format_view_count
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
                            max_lines=1,
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
                            f"{format_view_count(video.view_count)} visualizações - "
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
        on_changed=None,
        tags=None
    ):
        super().__init__()

        self.video = video
        self.page = page
        self.on_changed = on_changed

        self.tags = tags or []

        self.width = 280
        self.alignment = ft.MainAxisAlignment.START

        self.controls = [
            # Thumbnail
            ft.Row(
                [
                    ft.Container(
                        width=280,
                        height=157.5,
                        border_radius=ft.border_radius.all(8),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        on_click=self.open_edit_video_dialog,
                        content=ft.Stack(
                            controls=[
                                ft.Image(
                                    src=video.thumbnail_path,
                                    width=280,
                                    height=157.5,
                                    fit=ft.ImageFit.COVER,
                                ),

                                ft.Container(
                                    right=6,
                                    bottom=6,
                                    bgcolor=ft.Colors.BLACK,
                                    opacity=0.85,
                                    padding=ft.padding.symmetric(
                                        horizontal=6,
                                        vertical=3
                                    ),
                                    border_radius=ft.border_radius.all(4),
                                    content=ft.Text(
                                        value=video.duration or "00:00",
                                        size=11,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD
                                    )
                                )
                            ]
                        )
                    )
                ]
            ),

            # Informações do vídeo
            ft.Row(
                [
                    ft.Container(
                        width=40,
                        height=40,
                        border_radius=20,
                        margin=ft.margin.only(top=2),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=(
                            ft.Image(
                                src=video.channel_thumbnail_path,
                                width=40,
                                height=40,
                                fit=ft.ImageFit.COVER
                            )
                            if video.channel_thumbnail_path
                            else ft.Container(
                                width=40,
                                height=40,
                                bgcolor=ft.Colors.GREY_700
                            )
                        )
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

        # Faixa de tags: somente aparece quando existem tags.
        if self.tags:
            self.controls.append(
                self.create_tags_bar()
            )

    def create_tags_bar(self):

        self.tags_list = ft.ListView(
            horizontal=True,
            spacing=5,
            padding=0,
            height=22,
            auto_scroll=False,
            controls=[
                ft.Container(
                    height=18,
                    margin=0,
                    padding=ft.padding.symmetric(
                        horizontal=9,
                        vertical=0
                    ),
                    alignment=ft.alignment.center,
                    bgcolor=tag["color"],
                    border_radius=5,
                    content=ft.Text(
                        value=tag["name"],
                        size=10,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        no_wrap=True,
                        style=ft.TextStyle(height=1.0)
                    )
                )
                for tag in self.tags
            ]
        )

        return ft.Row(
            height=24,
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_size=19,
                    width=22,
                    height=24,
                    padding=0,
                    on_click=self.scroll_tags_left
                ),

                ft.Container(
                    expand=True,
                    height=22,
                    padding=0,
                    content=self.tags_list
                ),

                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    icon_size=19,
                    width=22,
                    height=24,
                    padding=0,
                    on_click=self.scroll_tags_right
                )
            ]
        )

    def scroll_tags_left(self, e):
        self.tags_list.scroll_to(
            delta=-160,
            duration=200
        )

    def scroll_tags_right(self, e):
        self.tags_list.scroll_to(
            delta=160,
            duration=200
        )

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
