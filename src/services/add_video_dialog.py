import flet as ft
from datetime import datetime
from models.tab import Tab
from components.modal_dialog import Dialog

def open_video_dialog(page: ft.Page):
    dlg = Dialog()
    page = page
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

# class OpenVideoDialog:
#     def __init__(self, page):
#         self.page = page
#         self._build_dialog()
        
#     def _build_dialog(self):
#         self.url_field = ft.TextField(label="URL do vídeo", autofocus=True)
#         self.title_field = ft.TextField(label="Título")
#         self.index_field = ft.TextField(label="Índice", input_filter=ft.NumbersOnlyInputFilter())
#         self.priority_field = ft.Dropdown(
#             label="Prioridade",
#             options=[
#                 ft.dropdown.Option("Alta"),
#                 ft.dropdown.Option("Média"),
#                 ft.dropdown.Option("Baixa"),
#             ]
#         )
#         self.tags_field = ft.TextField(label="Tags (separadas por vírgula)")
#         self.active_switch = ft.Switch(label="Ativo", value=True)

#         self.dialog = ft.AlertDialog(
#             modal=True,
#             title=ft.Text("Adicionar novo vídeo"),
#             content=ft.Column(
#                 controls=[
#                     self.url_field,
#                     self.title_field,
#                     self.index_field,
#                     self.priority_field,
#                     self.tags_field,
#                     self.active_switch,
#                 ],
#                 tight=True,
#                 scroll=ft.ScrollMode.AUTO,
#                 height=400,
#             ),
#             actions=[
#                 ft.TextButton("Cancelar", on_click=self.close),
#                 ft.TextButton("Salvar", on_click=self.save),
#             ],
#             actions_alignment=ft.MainAxisAlignment.END,
#         )
    
#     def open(self):
#         self.page.dialog = self.dialog
#         self.dialog.open = True
#         self.page.update()
    
#     def close(self, e):
#         self.dialog.open = False
#         self.page.update()
    
#     def save(self, e):
#         new_tab = Tab(
#             url=self.url_field.value,
#             title=self.title_field.value,
#             index=int(self.index_field.value) if self.index_field.value else 0,
#             priority=self.priority_field.value,
#             create_at=datetime.now(),
#             tags=[tag.strip() for tag in self.tags_field.value.split(",")] if self.tags_field.value else [],
#             active=self.active_switch.value
#         )
#         print("Novo vídeo adicionado:", new_tab)
#         self.close(e)
#         # Aqui você pode chamar o controller para salvar