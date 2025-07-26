import flet as ft
from components.modal_dialog import Dialog

def open_video_dialog(page: ft.Page):
    dlg = Dialog()
    page = page
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
