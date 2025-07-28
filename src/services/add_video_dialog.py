import flet as ft
from components.modal_dialog import Dialog

def open_video_dialog(page: ft.Page, callback=None):
    dlg = Dialog(callback)
    page = page
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
