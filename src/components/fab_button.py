import flet as ft
from services.add_video_dialog import open_video_dialog

class FABButton(ft.FloatingActionButton):
    def __init__(self, page):
        super().__init__()
        self.icon = ft.Icons.ADD
        self.bgcolor = ft.Colors.BLUE
        self.on_click = lambda x: open_video_dialog(page)
        tooltip = "Adicionar novo vídeo"
