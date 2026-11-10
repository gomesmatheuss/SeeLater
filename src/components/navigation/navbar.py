import flet as ft

class PopupColorItem(ft.PopupMenuItem):
    def __init__(self, color, name):
        super().__init__()
        self.content = ft.Row(
            controls = [
                ft.Icon(name=ft.Icons.COLOR_LENS_OUTLINED, color=color),
                ft.Text(name),
            ],
        )
        self.on_click = self.seed_color_changed
        self.data = color

    def seed_color_changed(self, e):
        self.page.theme = self.page.dark_theme = ft.Theme(color_scheme_seed=self.data)
        self.page.update()


class ThemeButton(ft.Column):
    def __init__(self):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.width = 60
        self.dark_light_icon = ft.IconButton(
            icon = ft.Icons.BRIGHTNESS_2_OUTLINED,
            icon_color = ft.Colors.PRIMARY,
            tooltip = "Toggle brightness",
            on_click = self.theme_changed,
        )
        self.controls = [
            self.dark_light_icon
        ]

    def theme_changed(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.dark_light_icon.icon = ft.Icons.BRIGHTNESS_HIGH
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.dark_light_icon.icon = ft.Icons.BRIGHTNESS_2
        self.page.update()


class SeedColorPicker(ft.Column):
    def __init__(self):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER
        self.controls = [
            ft.PopupMenuButton(
                icon = ft.Icons.COLOR_LENS_OUTLINED,
                icon_color = ft.Colors.PRIMARY,
                items=[
                    PopupColorItem(color="deeppurple", name="Deep purple (default)"),
                    PopupColorItem(color="indigo", name="Indigo"),
                    PopupColorItem(color="blue", name="Blue"),
                    PopupColorItem(color="teal", name="Teal"),
                    PopupColorItem(color="green", name="Green"),
                    PopupColorItem(color="yellow", name="Yellow"),
                    PopupColorItem(color="orange", name="Orange"),
                    PopupColorItem(color="deeporange", name="Deep orange"),
                    PopupColorItem(color="pink", name="Pink")
                ]
            )
        ]


class Navbar(ft.AppBar):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.INVERSE_PRIMARY
        self.actions = [
            SeedColorPicker(),
            ThemeButton()
        ]
