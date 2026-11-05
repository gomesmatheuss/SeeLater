
import flet as ft


class LeftNavigationMenu(ft.Column):
    def __init__(self, on_navigate):
        super().__init__()

        self.on_navigate = on_navigate
        self.selected_page = "home"

        self.width = 150
        self.spacing = 8
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        self.build_menu()

    def navigation_item(self, title, icon, page_key):
        selected = self.selected_page == page_key

        return ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=(
                ft.Colors.PRIMARY_CONTAINER
                if selected
                else None
            ),
            on_click=lambda e: self.on_navigate(page_key),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        icon,
                        color=(
                            ft.Colors.ON_PRIMARY_CONTAINER
                            if selected
                            else ft.Colors.ON_SURFACE
                        )
                    ),
                    ft.Text(
                        title,
                        color=(
                            ft.Colors.ON_PRIMARY_CONTAINER
                            if selected
                            else ft.Colors.ON_SURFACE
                        )
                    )
                ]
            )
        )

    def build_menu(self):
        self.controls = [
            ft.Container(
                padding=10,
                content=ft.Text(
                    "SeeLater",
                    size=20,
                    weight=ft.FontWeight.BOLD
                )
            ),

            self.navigation_item(
                "Início",
                ft.Icons.HOME_OUTLINED,
                "home"
            ),

            self.navigation_item(
                "Tags",
                ft.Icons.LABEL_OUTLINE,
                "tags"
            ),

            self.navigation_item(
                "Grupos",
                ft.Icons.FOLDER_OUTLINED,
                "groups"
            )
        ]

    def set_selected(self, page_key):
        self.selected_page = page_key
        self.build_menu()
        self.update()
