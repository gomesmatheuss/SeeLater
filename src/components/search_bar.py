import flet as ft

class SearchBar(ft.Row):
    def __init__(self, on_search):
        super().__init__()
        self.on_search = on_search
        self.bar = ft.SearchBar(
            view_elevation = 4,
            divider_color = ft.Colors.AMBER,
            bar_bgcolor = ft.Colors.SECONDARY_CONTAINER,
            bar_hint_text = "Search url, title, tags...",
            # view_hint_text  ="Choose a color from the suggestions...",
            height = 40,
            width = 500,
            # on_change=handle_change,
            # on_submit=handle_submit,
            # on_tap=handle_tap,
        )
        self.button = ft.ElevatedButton(
            icon = ft.Icons.SEARCH_SHARP,
            text = "Search",
            height = 40,
            width = 100,
            elevation = 4,
            bgcolor = ft.Colors.PRIMARY_CONTAINER,
            on_click = self.on_search_click
        )

        self.height = 60
        self.alignment = ft.MainAxisAlignment.CENTER
        self.controls = [
            self.bar,
            self.button
        ]

    def on_search_click(self, e):
        self.on_search(self.bar.value)
