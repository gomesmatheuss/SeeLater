import flet as ft
from components.video_card import Card
from components.fab_button import FABButton
from components.grid_pagination import GridPagination
from services.grid_service import GridService


class Grid(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.search_term = ""
        self.items_per_page = 54

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

        self.pagination_controls = GridPagination(
            on_page_change=self.on_page_change,
            current_page=0,
            total_items=0,
            items_per_page=self.items_per_page
        )

        self.controls = [
            self.cards_row,
            self.pagination_controls
        ]

        self.update_cards()

    def on_video_added(self):
        self.update_cards(
            hard_refresh=True
        )

    def on_page_change(self, page):

        self.update_cards(
            change_page=True
        )

    def update_cards(
        self,
        search_term="",
        change_page=False,
        hard_refresh=False
    ):

        if not change_page:
            self.search_term = search_term
            self.pagination_controls.current_page = 0

        current_page = self.pagination_controls.current_page

        videos = self.service.get_page_videos(
            current_page=current_page,
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

        total_items = self.service.get_total_items(
            self.search_term
        )

        self.pagination_controls.set_data(
            current_page=current_page,
            total_items=total_items
        )

        self.page.update()
