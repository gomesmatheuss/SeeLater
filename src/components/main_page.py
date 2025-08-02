import flet as ft
from components.left_navigation_menu import LeftNavigationMenu
from components.grid import Grid
from components.search_bar import SearchBar

class MainPage(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.left_nav = LeftNavigationMenu()
        self.grid = Grid(page)
        self.search_bar = SearchBar(on_search=self.on_search)

        self.expand = True
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            self.left_nav,
            ft.VerticalDivider(width=1),
            ft.Column([
                self.search_bar,
                self.grid
            ],
            expand=True)
        ]

    def on_search(self, query):
        self.grid.update_cards(query)
