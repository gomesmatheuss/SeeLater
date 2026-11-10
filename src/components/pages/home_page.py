
import flet as ft

from components.grid import Grid
from components.search_bar import SearchBar

from components.group_items.import_group_items_dialog import ImportGroupItemsDialog


class HomePage(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.grid = Grid(page)

        self.search_bar = SearchBar(
            on_search=self.on_search
        )

        self.import_button = ft.ElevatedButton(
            "Importar itens",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.open_import_dialog
        )

        self.header = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.import_button
            ]
        )

        self.expand = True
        self.spacing = 5

        self.controls = [
            self.header,
            self.search_bar,
            self.grid
        ]

    def on_search(self, query):
        self.grid.update_cards(query)

    def open_import_dialog(self, e):

        dialog = ImportGroupItemsDialog(
            group=None,
            existing_items=[],
            on_import_complete=lambda: self.grid.update_cards(
                hard_refresh=True
            )
        )

        self.page.open(dialog)
