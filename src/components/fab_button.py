import flet as ft
from components.add_links_alertdialog import AddLinks


class FABButton(ft.FloatingActionButton):
    def __init__(self, page: ft.Page, on_video_added):
        super().__init__()

        self.page = page
        self.on_video_added = on_video_added

        self.icon = ft.Icons.ADD
        self.bgcolor = ft.Colors.BLUE
        self.tooltip = "Adicionar novo vídeo"
        self.on_click = self.on_click_handler

    def on_click_handler(self, e):
        self.open_video_dialog()

    def open_video_dialog(self):
        def after_dialog(result):
            if self.on_video_added:
                self.on_video_added()

        dlg = AddLinks(after_dialog)

        self.page.overlay.append(dlg)
        dlg.open = True

        self.page.update()
