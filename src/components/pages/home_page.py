
import flet as ft
from components.grid import Grid
from components.search_bar import SearchBar


class HomePage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.grid = Grid(page)
        self.search_bar = SearchBar(
            on_search=self.on_search
        )

        self.expand = True
        self.spacing = 0

        self.controls = [
            self.search_bar,
            self.grid
        ]

    def on_search(self, query):
        self.grid.update_cards(query)
