
import re
import flet as ft

from components.add_tag_dialog import AddTagDialog
from services.db_service import (
    get_all_tags_with_usage,
    save_tag,
    update_tag,
    delete_tag
)


class TagsPage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.tag_dialog = AddTagDialog(
            self.page,
            on_saved=self.load_tags
        )

        self.expand = True
        self.spacing = 15
        self.scroll = ft.ScrollMode.AUTO

        self.tags_list = ft.Column(
            spacing=10,
            expand=True
        )

        self.controls = [
            ft.Container(
                expand=True,
                padding=ft.padding.only(
                    left=20,
                    right=20,
                    top=15,
                    bottom=15
                ),
                content=ft.Column(
                    expand=True,
                    spacing=15,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(
                                    spacing=3,
                                    controls=[
                                        ft.Text(
                                            "Gerenciar tags",
                                            size=24,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Text(
                                            "Organize seus vídeos utilizando tags."
                                        )
                                    ]
                                ),
                                ft.Button(
                                    "Nova tag",
                                    icon=ft.Icons.ADD,
                                    on_click=self.open_new_tag_dialog
                                )
                            ]
                        ),
                        ft.Divider(),
                        self.tags_list
                    ]
                )
            )
        ]

        self.load_tags()

    def load_tags(self):
        self.tags_list.controls.clear()

        tags = get_all_tags_with_usage()

        if not tags:
            self.tags_list.controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(
                                ft.Icons.LABEL_OUTLINE,
                                size=45,
                                color=ft.Colors.OUTLINE
                            ),
                            ft.Text(
                                "Nenhuma tag cadastrada.",
                                color=ft.Colors.OUTLINE
                            ),
                            ft.Text(
                                "Clique em 'Nova tag' para começar."
                            )
                        ]
                    )
                )
            )

        else:
            for tag in tags:
                self.tags_list.controls.append(
                    self.create_tag_item(tag)
                )


    def create_tag_item(self, tag):

        tag_color = tag.get("color") or "#2196F3"
        description = tag.get("description") or "Sem descrição"

        return ft.Container(
            padding=15,
            border=ft.border.all(
                1,
                ft.Colors.OUTLINE_VARIANT
            ),
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=14,
                                height=14,
                                border_radius=7,
                                bgcolor=tag_color
                            ),
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        tag["name"],
                                        weight=ft.FontWeight.BOLD,
                                        size=16
                                    ),
                                    ft.Text(
                                        description,
                                        color=ft.Colors.OUTLINE,
                                        size=12
                                    ),
                                    ft.Text(
                                        f'{tag.get("usage_count", 0)} vídeos associados',
                                        color=ft.Colors.SECONDARY,
                                        size=11
                                    )
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar tag",
                                on_click=lambda e, t=tag: self.open_edit_tag_dialog(t)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Excluir tag",
                                icon_color=ft.Colors.ERROR,
                                on_click=lambda e, t=tag: self.confirm_delete_tag(t)
                            )
                        ]
                    )
                ]
            )
        )

    def open_new_tag_dialog(self, e):
        self.tag_dialog.open()

    def open_edit_tag_dialog(self, tag):
        self.tag_dialog.open(tag)

    def confirm_delete_tag(self, tag):

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir tag"),
            content=ft.Text(
                f'Deseja realmente excluir a tag "{tag["name"]}"? '
                "Ela também será removida dos vídeos associados."
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.close_dialog(dialog)
                ),
                ft.Button(
                    "Excluir",
                    color=ft.Colors.ERROR,
                    on_click=lambda e: self.remove_tag(dialog, tag)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.show_dialog(dialog)

    def remove_tag(self, dialog, tag):

        try:
            delete_tag(str(tag["_id"]))

            self.close_dialog(dialog)
            self.load_tags()

        except Exception as ex:
            print(f"Erro ao excluir tag: {ex}")

        self.page.update()

    def show_dialog(self, dialog):
        self.page.open(dialog)


    def close_dialog(self, dialog):
        self.page.close(dialog)
