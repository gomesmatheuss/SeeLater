import flet as ft
from components.video_card import Card
from services.video_service import load_card_info
from services.db_service import get_tabs_list, get_all_videos
from services.add_video_dialog import open_video_dialog

class FABButton(ft.FloatingActionButton):
    def __init__(self, page: ft.Page, grid):
        super().__init__()
        self.page = page
        self.grid = grid
        self.icon = ft.Icons.ADD
        self.bgcolor = ft.Colors.BLUE
        self.tooltip = "Adicionar novo vídeo"
        self.on_click = self.on_click_handler

    def on_click_handler(self, e):
        def after_dialog(result):
            self.grid.update_cards(hard_refresh=True)

        open_video_dialog(self.page, callback=after_dialog)


class Grid(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.current_page = 0
        self.items_per_page = 54
        self.search_term = ''
        self.ALL_TABS = []
        self.ALL_VIDEOS = {}

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.page.floating_action_button = FABButton(self.page, self)

        self.cards_row = ft.Row(
            spacing = 15,
            run_spacing = 15,
            wrap = True,
            vertical_alignment = ft.CrossAxisAlignment.START
        )

        self.pagination_controls = ft.Row(
            controls=[
                ft.TextButton("Anterior", on_click=self.previous_page),
                ft.TextButton("Próximo", on_click=self.next_page)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.controls = [
            self.cards_row,
            self.pagination_controls
        ]

        self.update_cards()

    def get_filtered_tabs(self, search_term: str, hard_refresh):
        if hard_refresh or not self.ALL_TABS:
            self.ALL_TABS = get_tabs_list()
            self.ALL_VIDEOS = get_all_videos()
        return [tab for tab in self.ALL_TABS if search_term.lower() in tab["title"].lower() or
                                       search_term.lower() in tab["url"].lower() or
                                       search_term in tab["tags"]]

    def get_all_tabs(self, search_term, hard_refresh):
        tabs = self.get_filtered_tabs(search_term, hard_refresh)
        cards = []
        for tab in tabs:
            video = load_card_info(tab, self.ALL_VIDEOS)
            if video:
                cards.append(Card(video))

        return cards

    def update_cards(self, search_term="", change_page=False, hard_refresh=False):
        if not change_page:
            self.search_term = search_term
            self.current_page = 0
        
        all_cards = self.get_all_tabs(self.search_term, hard_refresh)

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        current_cards = all_cards[start:end]

        self.cards_row.controls = current_cards
        self.page.update()

    def next_page(self, e):
        self.current_page += 1
        self.update_cards(change_page=True)

    def previous_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
        self.update_cards(change_page=True)
