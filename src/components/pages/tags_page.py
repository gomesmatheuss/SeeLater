
import re
import flet as ft

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
        self.open_tag_dialog()

    def open_edit_tag_dialog(self, tag):
        self.open_tag_dialog(tag)

    def open_tag_dialog(self, tag=None):

        is_editing = tag is not None

        name_field = ft.TextField(
            label="Nome da tag",
            value=tag.get("name", "") if is_editing else "",
            autofocus=True
        )

        description_field = ft.TextField(
            label="Descrição",
            value=tag.get("description", "") if is_editing else "",
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        color_field = ft.TextField(
            label="Cor personalizada (HEX)",
            value=tag.get("color", "#2196F3") if is_editing else "#2196F3",
            hint_text="#2196F3",
            expand=True
        )

        # Prévia da cor
        color_preview = ft.Container(
            width=30,
            height=30,
            border_radius=15,
            bgcolor=None,
            border=ft.border.all(2, ft.Colors.OUTLINE)
        )

        # Cores sugeridas
        suggested_colors = [
            "#2196F3",
            "#03A9F4",
            "#00BCD4",
            "#009688",
            "#4CAF50",
            "#8BC34A",
            "#CDDC39",
            "#FFC107",
            "#FF9800",
            "#FF5722",
            "#F44336",
            "#E91E63",
            "#9C27B0",
            "#673AB7",
            "#795548",
            "#607D8B",
        ]

        palette_items = []

        def update_palette_highlight():
            current_color = (color_field.value or "").strip().upper()

            for color, item in palette_items:
                selected = current_color == color.upper()

                item.border = ft.border.all(
                    3 if selected else 1,
                    ft.Colors.PRIMARY if selected
                    else ft.Colors.OUTLINE_VARIANT
                )

        def update_color_preview():
            color = (color_field.value or "").strip()

            if re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
                color_preview.bgcolor = color
            else:
                color_preview.bgcolor = None

        # Evento de digitação: atualiza tudo
        def on_color_change(e):
            update_palette_highlight()
            update_color_preview()
            self.page.update()

        color_field.on_change = on_color_change

        # Seleção de uma cor sugerida
        def select_color(color):
            color_field.value = color

            update_palette_highlight()
            update_color_preview()

            self.page.update()

        # Montagem da paleta
        for color in suggested_colors:

            color_item = ft.Container(
                width=30,
                height=30,
                bgcolor=color,
                border_radius=15,
                border=ft.border.all(
                    1,
                    ft.Colors.OUTLINE_VARIANT
                ),
                on_click=lambda e, c=color: select_color(c),
                tooltip=color
            )

            palette_items.append((color, color_item))

        color_palette = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=[
                item for color, item in palette_items
            ]
        )

        # Estado inicial da prévia
        update_palette_highlight()
        update_color_preview()

        error_text = ft.Text(
            color=ft.Colors.ERROR,
            size=12
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar tag" if is_editing else "Nova tag"
            ),
            content=ft.Column(
                tight=True,
                width=400,
                spacing=12,
                controls=[
                    name_field,
                    description_field,

                    ft.Text(
                        "Sugestões de cores",
                        weight=ft.FontWeight.BOLD,
                        size=13
                    ),

                    color_palette,

                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            color_field,
                            color_preview
                        ]
                    ),

                    error_text
                ]
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.close_dialog(dialog)
                ),
                ft.Button(
                    "Salvar",
                    on_click=lambda e: self.save_tag_dialog(
                        dialog,
                        name_field,
                        description_field,
                        color_field,
                        error_text,
                        tag
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.show_dialog(dialog)

    def save_tag_dialog(
        self,
        dialog,
        name_field,
        description_field,
        color_field,
        error_text,
        tag=None
    ):

        name = name_field.value.strip()
        description = description_field.value.strip()
        color = color_field.value.strip()

        if not name:
            error_text.value = "Informe o nome da tag."
            self.page.update()
            return

        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            error_text.value = "Informe uma cor HEX válida. Exemplo: #2196F3"
            self.page.update()
            return

        try:
            if tag:
                update_tag(
                    str(tag["_id"]),
                    name,
                    color,
                    description
                )
            else:
                save_tag(
                    name,
                    color,
                    description
                )

            self.close_dialog(dialog)
            self.load_tags()

        except Exception as ex:
            error_text.value = str(ex)
            self.page.update()

        self.page.update()

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
