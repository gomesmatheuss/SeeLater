
import flet as ft

from services.group_service import GroupService
from services.db_service import delete_group

from components.group_card import GroupCard
from components.add_group_alertdialog import AddGroupDialog
from components.edit_group_alertdialog import EditGroupDialog


class GroupsPage(ft.Column):

    def __init__(self, page: ft.Page, on_open_group=None):
        super().__init__()

        self.page = page
        self.app_page = page

        self.on_open_group = on_open_group

        self.service = GroupService()

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.groups_row = ft.Row(
            spacing=15,
            run_spacing=20,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.ElevatedButton(
                        "Adicionar grupo",
                        icon=ft.Icons.ADD,
                        on_click=self.open_add_dialog
                    )
                ]
            ),
            self.groups_row
        ]

        self.update_groups()

    def update_groups(self, hard_refresh=False):

        groups = self.service.get_groups(
            hard_refresh=hard_refresh
        )

        cards = []

        for group in groups:

            preview_items = self.service.get_group_preview(
                str(group["_id"]),
                limit=4
            )

            cards.append(
                GroupCard(
                    group=group,
                    preview_items=preview_items,
                    on_click=self.open_group,
                    on_edit=self.open_edit_dialog,
                    on_delete=self.confirm_delete_group
                )
            )

        self.groups_row.controls = cards

        self.app_page.update()

    # =========================
    # CRIAR GRUPO
    # =========================

    def open_add_dialog(self, e):

        dialog = AddGroupDialog(
            on_created=self.on_group_created
        )

        self.page.open(dialog)

    def on_group_created(self):

        self.service.invalidate_cache()

        self.update_groups(hard_refresh=True)

        self.page.open(
            ft.SnackBar(
                content=ft.Text("Grupo criado com sucesso!"),
                open=True
            )
        )

    # =========================
    # EDITAR GRUPO
    # =========================

    def open_edit_dialog(self, group):

        dialog = EditGroupDialog(
            group=group,
            on_updated=self.on_group_updated
        )

        self.page.open(dialog)

    def on_group_updated(self):

        self.service.invalidate_cache()

        self.update_groups(hard_refresh=True)

        self.page.open(
            ft.SnackBar(
                content=ft.Text("Grupo atualizado com sucesso!"),
                open=True
            )
        )

    # =========================
    # EXCLUIR GRUPO
    # =========================

    def confirm_delete_group(self, group):

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir grupo"),
            content=ft.Text(
                f'Deseja realmente excluir o grupo "{group["name"]}"?'
                "\n\nOs vídeos não serão excluídos."
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.page.close(dialog)
                ),
                ft.ElevatedButton(
                    "Excluir",
                    color=ft.Colors.RED,
                    on_click=lambda e: self.delete_group_confirmed(
                        group,
                        dialog
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.open(dialog)

    def delete_group_confirmed(self, group, dialog):

        delete_group(str(group["_id"]))

        self.page.close(dialog)

        self.service.invalidate_cache()

        self.update_groups(hard_refresh=True)

        self.page.open(
            ft.SnackBar(
                content=ft.Text("Grupo excluído com sucesso!"),
                open=True
            )
        )

    # =========================
    # ABRIR GRUPO
    # =========================

    def open_group(self, group):

        if self.on_open_group:
            self.on_open_group(group)
