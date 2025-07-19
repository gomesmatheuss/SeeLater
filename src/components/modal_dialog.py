import flet as ft
from models.tab import Tab
from services.load_from_json import process_json
from datetime import datetime

class Dialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.url_field = ft.TextField(label="URL do vídeo", autofocus=True)
        self.priority_field = ft.Dropdown(
            label = "Prioridade",
            width = 300,
            options=[
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Baixa"),
            ],
            value = "Baixa"
        )
        self.tags_field = ft.TextField(label="Tags (separadas por vírgula)")
        self.upload_button = ft.OutlinedButton(
            text = "Selecione um arquivo", 
            height = 30,
            icon = ft.Icons.UPLOAD_FILE,
            on_click = self.pick_files
        )
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_files = ft.Text(size=10, color=ft.Colors.GREEN)

        self.modal = True
        self.title = ft.Text("Adicionar novo vídeo")
        self.content = ft.Column(
            controls = [
                self.url_field,
                self.priority_field,
                self.tags_field,
                ft.Divider(height=35),
                ft.Row(
                    [
                        ft.Text("ou com .json"),
                        self.upload_button
                    ]
                ),
                self.selected_files
            ],
            tight = True,
            height = 250,
            width = 400
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
            url = self.url_field.value,
            title = "",
            index = 0,
            priority = self.priority_field.value,
            create_at = datetime.now(),
            tags = [tag.strip() for tag in self.tags_field.value.split(",")] if self.tags_field.value else [],
            active = True
        )
        print("Novo vídeo adicionado:", new_tab.__dict__)
        self.close(e)

    def pick_files(self, e):
        self.pick_files_dialog.pick_files(allowed_extensions=["json", "txt"], allow_multiple=False)

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        self.selected_files.value = (
            json_path := f"{e.files[0].path}" if e.files else ""
        )
        self.selected_files.update()

        if json_path:
            process_json(json_path)
            self.close(e)

    def did_mount(self):
        self.page.overlay.append(self.pick_files_dialog)
        self.page.update()

    def will_unmount(self):
        self.page.overlay.remove(self.pick_files_dialog)
        self.page.update()
