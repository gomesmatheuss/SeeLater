import flet as ft
from models.tab import Tab
from datetime import datetime

class Dialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.url_field = ft.TextField(label="URL do vídeo", autofocus=True)
        self.title_field = ft.TextField(label="Título")
        self.index_field = ft.TextField(label="Índice", input_filter=ft.NumbersOnlyInputFilter())
        self.priority_field = ft.Dropdown(
            label = "Prioridade",
            width = 300,
            options=[
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Baixa"),
            ]
        )
        self.tags_field = ft.TextField(label="Tags (separadas por vírgula)")
        self.active_switch = ft.Switch(label="Ativo", value=True)

        self.modal = True
        self.title = ft.Text("Adicionar novo vídeo")
        self.content = ft.Column(
            controls = [
                self.url_field,
                self.title_field,
                self.index_field,
                self.priority_field,
                self.tags_field,
                self.active_switch
            ],
            tight = True,
            height = 400,
            width = 600
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close),
            ft.TextButton("Salvar", on_click=self.save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def close(self, e):
        self.open = False
        self.page.update()

    def save(self, e):
        new_tab = Tab(
            url=self.url_field.value,
            title=self.title_field.value,
            index=int(self.index_field.value) if self.index_field.value else 0,
            priority=self.priority_field.value,
            create_at=datetime.now(),
            tags=[tag.strip() for tag in self.tags_field.value.split(",")] if self.tags_field.value else [],
            active=self.active_switch.value
        )
        print("Novo vídeo adicionado:", new_tab.__dict__)
        self.close(e)
