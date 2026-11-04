
import flet as ft

from components.left_navigation_menu import LeftNavigationMenu
from components.pages.home_page import HomePage
from components.pages.tags_page import TagsPage


class MainPage(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        # Páginas
        self.home_page = HomePage(page)
        self.tags_page = TagsPage(page)

        # Guarda o botão flutuante criado pelo Grid
        self.home_fab = page.floating_action_button

        # Menu lateral
        self.left_nav = LeftNavigationMenu(
            on_navigate=self.navigate
        )

        # Área onde as páginas serão exibidas
        self.content_area = ft.Container(
            expand=True,
            content=self.home_page
        )

        self.expand = True
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 0

        self.controls = [
            self.left_nav,
            ft.VerticalDivider(width=1),
            self.content_area
        ]

    def navigate(self, page_key):

        if page_key == "home":
            self.content_area.content = self.home_page
            self.page.floating_action_button = self.home_fab

        elif page_key == "tags":
            self.content_area.content = self.tags_page
            self.page.floating_action_button = None

        self.left_nav.set_selected(page_key)

        self.page.update()
