import flet as ft
from navbar import Navbar
from grid2 import Grid

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
        Grid()
    )

ft.app(main)
