
import flet as ft


class BulkTagsDialog:

    def __init__(self, import_dialog):
        self.dialog = import_dialog

        self.checkboxes = []
        self.apply_to_all = None
        self.error_text = None

    def open(self, e=None):

        dialog = self.dialog

        self.checkboxes = []

        for tag in dialog.available_tags:

            checkbox = ft.Checkbox(
                label=tag["name"],
                value=False
            )

            self.checkboxes.append((tag, checkbox))

        self.apply_to_all = ft.Checkbox(
            label="Aplicar alterações para todos os itens importados",
            value=False
        )

        selected_count = sum(
            1 for item in dialog.items
            if item["selected"] and not item["duplicate"]
        )

        selection_count_text = ft.Text(
            f"{selected_count} itens selecionados",
            size=13,
            color=ft.Colors.GREEN_400
        )

        self.error_text = ft.Text(
            color=ft.Colors.ERROR,
            size=12
        )

        if not self.checkboxes:

            editor_content = ft.Text(
                "Nenhuma tag cadastrada.",
                color=ft.Colors.GREY_400
            )

        else:

            editor_content = ft.Column(
                spacing=5,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=14,
                                height=14,
                                border_radius=7,
                                bgcolor=tag.get("color") or "#2196F3"
                            ),
                            checkbox
                        ]
                    )
                    for tag, checkbox in self.checkboxes
                ]
            )

        dialog.title = ft.Text(
            "Editar Tags dos itens selecionados",
            size=18
        )

        dialog.content = ft.Container(
            width=400,
            height=390,
            content=ft.Column(
                spacing=12,
                controls=[
                    selection_count_text,
                    ft.Divider(height=5),
                    editor_content,
                    ft.Divider(height=5),
                    self.apply_to_all,
                    self.error_text
                ]
            )
        )

        dialog.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: self.close()
            ),
            ft.OutlinedButton(
                "Remover",
                icon=ft.Icons.REMOVE,
                style=ft.ButtonStyle(
                    color=ft.Colors.RED_400,
                    padding=ft.padding.symmetric(horizontal=18)
                ),
                on_click=lambda e: self.save("remove")
            ),
            ft.OutlinedButton(
                "Adicionar",
                icon=ft.Icons.ADD,
                style=ft.ButtonStyle(
                    color=ft.Colors.GREEN_400,
                    padding=ft.padding.symmetric(horizontal=18)
                ),
                on_click=lambda e: self.save("add")
            )
        ]

        dialog.page.update()

    def close(self):

        dialog = self.dialog

        dialog.title = dialog.preview_title
        dialog.content = dialog.preview_content
        dialog.actions = dialog.preview_actions

        dialog.page.update()

    def save(self, action):

        dialog = self.dialog

        selected_tags = [
            tag["name"]
            for tag, checkbox in self.checkboxes
            if checkbox.value
        ]

        if not selected_tags:
            self.error_text.value = "Selecione pelo menos uma tag."
            dialog.content.content.spacing = 6
            dialog.content.height = 405
            dialog.page.update()
            return

        if self.apply_to_all.value:
            target_items = [
                item for item in dialog.items
                if not item["duplicate"]
            ]

        else:
            target_items = [
                item for item in dialog.items
                if item["selected"] and not item["duplicate"]
            ]

        if not target_items:
            self.error_text.value = (
                "Nenhum item selecionado. "
                "Marque os itens ou aplique à lista inteira."
            )
            dialog.content.content.spacing = 6
            dialog.content.height = 405
            dialog.page.update()
            return

        for item in target_items:

            current_tags = item.get("tags", [])

            if action == "add":

                for tag_name in selected_tags:

                    if tag_name not in current_tags:
                        current_tags.append(tag_name)

            elif action == "remove":

                current_tags = [
                    tag_name
                    for tag_name in current_tags
                    if tag_name not in selected_tags
                ]

            item["tags"] = current_tags

        self.close()
        dialog.content.height = 390
        dialog.update_preview()
