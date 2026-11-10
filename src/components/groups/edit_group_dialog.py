
import flet as ft

from services.db_service import update_group


class EditGroupDialog(ft.AlertDialog):

    def __init__(self, group: dict, on_updated=None):
        super().__init__()

        self.group = group
        self.on_updated = on_updated

        self.name_field = ft.TextField(
            label="Nome do grupo",
            value=group.get("name", ""),
            autofocus=True,
            max_length=100
        )

        self.description_field = ft.TextField(
            label="Descrição",
            value=group.get("description", ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
            max_length=300
        )

        self.title = ft.Text("Editar grupo")

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
                "Salvar",
                on_click=self.save
            )
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def cancel(self, e):
        self.page.close(self)

    def save(self, e):

        name = (self.name_field.value or "").strip()

        description = (
            self.description_field.value or ""
        ).strip()

        if not name:
            self.name_field.error_text = "Informe um nome."
            self.name_field.update()
            return

        try:
            update_group(
                group_id=str(self.group["_id"]),
                name=name,
                description=description
            )

        except ValueError as error:
            self.name_field.error_text = str(error)
            self.name_field.update()
            return

        self.page.close(self)

        if self.on_updated:
            self.on_updated()
