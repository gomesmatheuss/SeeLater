import flet as ft
from datetime import datetime
from components.grid import Grid
from components.navbar import Navbar
from components.fab_button import FABButton

class Tab:
    def __init__(self, url: str, title: str, index: int, priority: str, create_at, tags=[], active=True):
        self.url = url
        self.title = title
        self.index = index
        self.priority = priority
        self.create_at = create_at
        self.tags = tags
        self.active = active

def main(page: ft.Page):
    page.title = "SeeLater"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.ON_SECONDARY

    page.window.width = 1080
    page.window.height = 720
    page.window.min_width = 480

    page.add(
        Navbar(),
        ft.Stack(
            [
                ft.Column([Grid()], expand=True),
                ft.Container(
                    FABButton(page),
                    alignment = ft.alignment.bottom_right, 
                    margin=20
                )
            ],
            expand = True
        )
    )

ft.app(main)
