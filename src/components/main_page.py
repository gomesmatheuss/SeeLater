
import flet as ft

from components.left_navigation_menu import LeftNavigationMenu

from components.pages.home_page import HomePage
from components.pages.tags_page import TagsPage
from components.pages.groups_page import GroupsPage
from components.pages.group_items_page import GroupItemsPage


class MainPage(ft.Row):

    def __init__(self, page):
        super().__init__()

        self.page = page

        self.home_page = HomePage(page)
        self.tags_page = TagsPage(page)

        self.groups_page = GroupsPage(
            page,
            on_open_group=self.open_group_items
        )

        self.group_items_page = None

        self.home_fab = page.floating_action_button

        self.left_nav = LeftNavigationMenu(
            on_navigate=self.navigate
        )

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

        elif page_key == "groups":

            self.content_area.content = self.groups_page
            self.page.floating_action_button = None

        self.left_nav.set_selected(page_key)

        self.page.update()

    def open_group_items(self, group):

        self.group_items_page = GroupItemsPage(
            page=self.page,
            group=group,
            on_back=self.back_to_groups
        )

        self.content_area.content = self.group_items_page

        self.page.floating_action_button = None

        self.page.update()

    def back_to_groups(self):

        # Primeiro, recoloca a página na interface.
        self.content_area.content = self.groups_page

        # Depois, atualiza os grupos.
        self.groups_page.update_groups(
            hard_refresh=True
        )

        self.page.floating_action_button = None

        self.page.update()
