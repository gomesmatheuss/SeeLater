
import flet as ft


class SearchBar(ft.Row):

    def __init__(self, on_search, on_add=None):
        super().__init__()

        self.on_search = on_search
        self.on_add = on_add

        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH_SHARP,
            icon_size=26,
            tooltip="Pesquisar",
            on_click=self.on_search_click
        )

        self.bar = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.Colors.AMBER,
            bar_bgcolor=ft.Colors.SECONDARY_CONTAINER,
            bar_hint_text="Search url, title, tags...",
            bar_trailing=[self.search_button],
            height=40,
            width=500,
        )

        self.add_button = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_size=24,
            icon_color=ft.Colors.WHITE,
            width=40,
            height=40,
            tooltip="Importar itens",
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                bgcolor=ft.Colors.GREEN_700,
            ),
            on_click=self.on_add_click
        )

        self.count_text = ft.Text(
            "0 - 0 | 0",
            size=14,
            color=ft.Colors.GREY_400,
            no_wrap=True
        )

        self.height = 60
        self.alignment = ft.MainAxisAlignment.START
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10

        self.controls = [
            self.add_button,
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=self.bar
            ),
            self.count_text
        ]

    def on_add_click(self, e):
        if self.on_add:
            self.on_add(e)

    def on_search_click(self, e):
        self.on_search(self.bar.value)

    def set_count(self, start, end, total):
        self.count_text.value = f"{start} - {end} | {total}"
