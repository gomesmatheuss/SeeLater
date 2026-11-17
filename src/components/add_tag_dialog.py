
import re
import flet as ft

from services.db_service import save_tag, update_tag


class AddTagDialog:

    def __init__(self, page, on_saved=None, on_closed=None):
        self.page = page
        self.on_saved = on_saved
        self.on_closed = on_closed

    def open(self, tag=None):

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

        color_preview = ft.Container(
            width=30,
            height=30,
            border_radius=15,
            bgcolor=None,
            border=ft.border.all(2, ft.Colors.OUTLINE)
        )

        suggested_colors = [
            "#2196F3", "#03A9F4", "#00BCD4", "#009688",
            "#4CAF50", "#8BC34A", "#CDDC39", "#FFC107",
            "#FF9800", "#FF5722", "#F44336", "#E91E63",
            "#9C27B0", "#673AB7", "#795548", "#607D8B",
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

        def on_color_change(e):
            update_palette_highlight()
            update_color_preview()
            self.page.update()

        color_field.on_change = on_color_change

        def select_color(color):
            color_field.value = color
            update_palette_highlight()
            update_color_preview()
            self.page.update()

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
                    on_click=lambda e: self.close(dialog)
                ),
                ft.Button(
                    "Salvar",
                    on_click=lambda e: self.save(
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

        self.page.open(dialog)

    def save(
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
            error_text.value = (
                "Informe uma cor HEX válida. Exemplo: #2196F3"
            )
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
                save_tag(name, color, description)

            self.close(dialog)

            if self.on_saved:
                self.on_saved()

            self.page.update()

        except Exception as ex:
            error_text.value = str(ex)
            self.page.update()

    def close(self, dialog):
        self.page.close(dialog)

        if self.on_closed:
            self.on_closed()
