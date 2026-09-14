import flet as ft
from components.video_card import Card
from components.fab_button import FABButton
from services.grid_service import GridService


class Grid(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.current_page = 0
        self.items_per_page = 54
        self.search_term = ""

        self.service = GridService()

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.page.floating_action_button = FABButton(
            self.page,
            self.on_video_added
        )

        self.cards_row = ft.Row(
            spacing=15,
            run_spacing=15,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.pagination_controls = ft.Row(
            controls=[
                ft.TextButton(
                    "Anterior",
                    on_click=self.previous_page
                ),
                ft.TextButton(
                    "Próximo",
                    on_click=self.next_page
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.controls = [
            self.cards_row,
            self.pagination_controls
        ]

        self.update_cards()

    def on_video_added(self):
        """
        Chamado quando um novo vídeo é adicionado.
        """

        self.current_page = 0

        self.update_cards(
            hard_refresh=True
        )

    def update_cards(
        self,
        search_term="",
        change_page=False,
        hard_refresh=False
    ):

        if not change_page:
            self.search_term = search_term
            self.current_page = 0

        videos = self.service.get_page_videos(
            current_page=self.current_page,
            items_per_page=self.items_per_page,
            search_term=self.search_term,
            hard_refresh=hard_refresh
        )

        cards = [
            Card(
                video,
                self.page,
                self
            )
            for video in videos
        ]

        self.cards_row.controls = cards

        self.page.update()

    def next_page(self, e):
        total_items = self.service.get_total_items(
            self.search_term
        )

        total_pages = max(
            1,
            (total_items + self.items_per_page - 1)
            // self.items_per_page
        )

        if self.current_page + 1 >= total_pages:
            return

        self.current_page += 1

        self.update_cards(
            change_page=True
        )

    def previous_page(self, e):
        if self.current_page <= 0:
            return

        self.current_page -= 1

        self.update_cards(
            change_page=True
        )
