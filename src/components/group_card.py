
import flet as ft

from services.utils import format_timestamp


class GroupCard(ft.Column):

    def __init__(
        self,
        group: dict,
        preview_items: list,
        on_click=None,
        on_edit=None,
        on_delete=None
    ):
        super().__init__()

        self.group = group
        self.preview_items = preview_items
        self.on_click_callback = on_click
        self.on_edit_callback = on_edit
        self.on_delete_callback = on_delete

        self.width = 280
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START

        self.controls = [
            self.create_thumbnail(),
            self.create_information()
        ]

    def create_thumbnail(self):

        items = self.preview_items[:4]

        images = [
            ft.Image(
                src=item.thumbnail_path,
                fit=ft.ImageFit.COVER,
                width=280,
                height=157.5
            )
            for item in items
        ]

        if not images:
            content = ft.Container(
                width=280,
                height=157.5,
                bgcolor=ft.Colors.GREY_800,
                alignment=ft.alignment.center,
                content=ft.Icon(
                    ft.Icons.VIDEO_LIBRARY_OUTLINED,
                    size=45,
                    color=ft.Colors.GREY_500
                )
            )

        elif len(images) == 1:
            content = images[0]

        elif len(images) == 2:
            content = ft.Row(
                spacing=2,
                controls=[
                    ft.Container(
                        expand=1,
                        height=157.5,
                        content=images[0]
                    ),
                    ft.Container(
                        expand=1,
                        height=157.5,
                        content=images[1]
                    )
                ]
            )

        else:
            quadrants = [
                ft.Container(
                    expand=1,
                    content=image
                )
                for image in images
            ]

            if len(quadrants) == 3:
                quadrants.append(
                    ft.Container(
                        expand=1,
                        bgcolor=ft.Colors.GREY_900
                    )
                )

            content = ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        spacing=2,
                        expand=1,
                        controls=quadrants[:2]
                    ),
                    ft.Row(
                        spacing=2,
                        expand=1,
                        controls=quadrants[2:4]
                    )
                ]
            )

        return ft.Container(
            width=280,
            height=157.5,
            border_radius=ft.border_radius.all(8),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=self.open_group,
            content=content
        )

    def create_information(self):

        name = self.group.get("name", "Sem nome")
        description = self.group.get("description", "")

        item_count = len(self.group.get("items", []))

        updated_at = self.group.get("updated_at")

        if updated_at:
            updated_text = format_timestamp(updated_at)
        else:
            updated_text = ""

        return ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(
                            value=name,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            tooltip=name
                        ),

                        ft.Text(
                            value=f"{item_count} itens",
                            size=11,
                            color=ft.Colors.GREY_400
                        ),

                        ft.Text(
                            value=description,
                            size=11,
                            color=ft.Colors.GREY_500,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            visible=bool(description)
                        ),

                        ft.Text(
                            value=f"Atualizado {updated_text}" if updated_text else "",
                            size=10,
                            color=ft.Colors.GREY_500
                        )
                    ]
                ),

                ft.PopupMenuButton(
                    padding=1,
                    menu_padding=1,
                    width=25,
                    items=[
                        ft.PopupMenuItem(
                            text="Editar",
                            height=30,
                            on_click=self.edit_group
                        ),

                        ft.PopupMenuItem(
                            text="Excluir",
                            height=30,
                            on_click=self.delete_group
                        )
                    ]
                )
            ]
        )

    def open_group(self, e):
        if self.on_click_callback:
            self.on_click_callback(self.group)

    def edit_group(self, e):
        if self.on_edit_callback:
            self.on_edit_callback(self.group)

    def delete_group(self, e):
        if self.on_delete_callback:
            self.on_delete_callback(self.group)
