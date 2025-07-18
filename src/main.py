import flet as ft
from components.grid import Grid
from components.navbar import Navbar
from components.fab_button import FABButton

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
