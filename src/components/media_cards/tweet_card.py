
import flet as ft
from services.utils import format_timestamp, format_view_count


class TweetCardTexts(ft.Column):

    def __init__(self, item: dict, page: ft.Page):
        super().__init__()

        self.item = item
        self.page = page

        self.spacing = 0
        self.expand = 1

        tweet_text = item.get("tweet_text") or "Descrição não disponível"
        author_name = item.get("author_name") or "Usuário do X"
        author_username = item.get("author_username") or ""

        if author_username and not author_username.startswith("@"):
            author_username = f"@{author_username}"

        self.controls = [
            # Descrição do tweet
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
                            value=tweet_text,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=13,
                            font_family="Roboto",
                            style=ft.TextStyle(height=1.2),
                            weight=ft.FontWeight.BOLD,
                            tooltip=ft.Tooltip(
                                tweet_text,
                                wait_duration=ft.Duration(
                                    milliseconds=600
                                )
                            )
                        )
                    )
                ]
            ),

            # Nome do autor e username
            ft.Row(
                height=16,
                expand=1,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(top=-4),
                        expand=1,
                        content=ft.Text(
                            value=(
                                f"{author_name} {author_username}"
                                if author_username
                                else author_name
                            ),
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=12,
                            font_family="Roboto",
                            color=ft.Colors.GREY_400,
                            tooltip=ft.Tooltip(
                                (
                                    f"{author_name} {author_username}"
                                    if author_username
                                    else author_name
                                ),
                                wait_duration=ft.Duration(
                                    milliseconds=600
                                )
                            )
                        )
                    )
                ]
            ),

            # Curtidas, reposts e data
            ft.Row(
                height=16,
                expand=1,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(top=-6),
                        expand=1,
                        content=ft.Text(
                            self.get_tweet_information(),
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

    def get_tweet_information(self):

        information = []

        like_count = self.item.get("like_count")
        repost_count = self.item.get("repost_count")
        tweet_date = self.item.get("tweet_date")

        if like_count is not None:
            information.append(
                f"{format_view_count(like_count)} curtidas"
            )

        if repost_count is not None:
            information.append(
                f"{format_view_count(repost_count)} reposts"
            )

        if tweet_date:
            information.append(
                format_timestamp(tweet_date)
            )

        return " - ".join(information) or "Informações indisponíveis"

    def copy_url_to_clipboard(self, e):

        url = self.item.get("url", "")

        if not url:
            return

        self.page.set_clipboard(url)

        self.page.open(
            ft.SnackBar(
                ft.Text(
                    f"Copied to clipboard: {url}"
                ),
                open=True
            )
        )


class TweetCard(ft.Column):

    def __init__(
        self,
        item: dict,
        page: ft.Page,
        tags=None
    ):
        super().__init__()

        self.item = item
        self.page = page

        self.tags = tags or []

        self.width = 280
        self.alignment = ft.MainAxisAlignment.START

        media_images = item.get("media_images") or []
        image_count = len(media_images)

        thumbnail_controls = [
            (
                ft.Image(
                    src=item["thumbnail_path"],
                    width=280,
                    height=157.5,
                    fit=ft.ImageFit.COVER
                )
                if item.get("thumbnail_path")
                else ft.Container(
                    width=280,
                    height=157.5,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    alignment=ft.alignment.center,
                    content=ft.Icon(
                        ft.Icons.IMAGE_OUTLINED,
                        size=55,
                        color=ft.Colors.GREY_500
                    )
                )
            )
        ]

        # Quantidade de fotos: aparece somente quando houver mais de uma.
        if image_count > 1:
            thumbnail_controls.append(
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
                        value=f"{image_count} fotos",
                        size=11,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD
                    )
                )
            )

        self.controls = [
            # Thumbnail
            ft.Row(
                [
                    ft.Container(
                        width=280,
                        height=157.5,
                        border_radius=ft.border_radius.all(8),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Stack(
                            controls=thumbnail_controls
                        )
                    )
                ]
            ),

            # Informações do tweet
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
                                src=item["author_profile_image_path"],
                                width=40,
                                height=40,
                                fit=ft.ImageFit.COVER
                            )
                            if item.get("author_profile_image_path")
                            else ft.Container(
                                width=40,
                                height=40,
                                bgcolor=ft.Colors.GREY_700,
                                alignment=ft.alignment.center,
                                content=ft.Icon(
                                    ft.Icons.PERSON,
                                    color=ft.Colors.GREY_400
                                )
                            )
                        )
                    ),

                    TweetCardTexts(item, page),

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
                                        on_click=self.action_not_available
                                    ),

                                    ft.PopupMenuItem(
                                        text="Mover Para o Topo",
                                        height=30,
                                        on_click=self.action_not_available
                                    ),

                                    ft.PopupMenuItem(
                                        text="Mover Para Último",
                                        height=30,
                                        on_click=self.action_not_available
                                    ),

                                    ft.PopupMenuItem(
                                        text="Carregar Informações",
                                        height=30,
                                        on_click=self.action_not_available
                                    ),

                                    ft.PopupMenuItem(
                                        text="Ocultar",
                                        height=30,
                                        on_click=self.action_not_available
                                    ),

                                    ft.PopupMenuItem(
                                        text="Excluir",
                                        height=30,
                                        on_click=self.action_not_available
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
                    bgcolor=ft.Colors.TRANSPARENT,
                    border=ft.border.all(1, tag["color"]),
                    border_radius=5,
                    content=ft.Text(
                        value=tag["name"],
                        size=10,
                        color=tag["color"],
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

    def action_not_available(self, e):

        self.page.open(
            ft.SnackBar(
                ft.Text(
                    "Esta ação ainda não está disponível para itens dos grupos."
                ),
                open=True
            )
        )
