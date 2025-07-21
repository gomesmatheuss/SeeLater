import flet as ft
from components.left_navigation_menu import LeftNavigationMenu
from components.grid import Grid

class MainPage(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.left_nav = LeftNavigationMenu()

        self.expand = True
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            self.left_nav,
            ft.VerticalDivider(width=1),
            Grid(page)
        ]
