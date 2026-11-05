
import flet as ft

from services.db_service import create_group


class AddGroupDialog(ft.AlertDialog):

    def __init__(self, on_created=None):
        super().__init__()

        self.on_created = on_created

        self.name_field = ft.TextField(
            label="Nome do grupo",
            autofocus=True,
            max_length=100
        )

        self.description_field = ft.TextField(
            label="Descrição",
            multiline=True,
            min_lines=2,
            max_lines=4,
            max_length=300
        )

        self.title = ft.Text("Novo grupo")

        self.content = ft.Column(
            tight=True,
            width=400,
            controls=[
                self.name_field,
                self.description_field
            ]
        )

        self.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=self.cancel
            ),
            ft.ElevatedButton(
                "Criar",
                on_click=self.create
            )
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def cancel(self, e):
        self.page.close(self)

    def create(self, e):

        name = self.name_field.value.strip()
        description = (
            self.description_field.value or ""
        ).strip()

        if not name:
            self.name_field.error_text = "Informe um nome."
            self.name_field.update()
            return

        try:
            create_group(name, description)

        except ValueError as error:
            self.name_field.error_text = str(error)
            self.name_field.update()
            return

        self.page.close(self)

        if self.on_created:
            self.on_created()
