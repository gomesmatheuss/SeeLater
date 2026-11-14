
import flet as ft

from components.grid import Grid
from components.search_bar import SearchBar

from components.importer.import_dialog import ImportItemsDialog


class HomePage(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.search_bar = SearchBar(
            on_search=self.on_search,
            on_add=self.open_import_dialog
        )

        self.grid = Grid(
            page,
            on_count_change=self.search_bar.set_count
        )

        self.expand = True
        self.spacing = 5

        self.controls = [
            ft.Container(
                content=self.search_bar,
                padding=ft.padding.symmetric(horizontal=15)
            ),
            self.grid
        ]

    def on_search(self, query):
        self.grid.update_cards(query)

    def open_import_dialog(self, e):

        dialog = ImportItemsDialog(
            group=None,
            existing_items=[],
            on_import_complete=lambda: self.grid.update_cards(
                hard_refresh=True
            )
        )

        self.page.open(dialog)
