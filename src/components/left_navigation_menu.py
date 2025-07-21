import flet as ft

class NavigationColumn(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = 4
        self.spacing = 0
        # self.scroll = ft.ScrollMode.ALWAYS
        self.width = 150
        # self.gallery = gallery
        # self.selected_index = 0
        # self.controls = self.get_navigation_items()
        self.controls = [ft.Text("Menu")]


class LeftNavigationMenu(ft.Column):
    def __init__(self):
        super().__init__()
        self.rail = NavigationColumn()

        self.controls = [
            self.rail
        ]
