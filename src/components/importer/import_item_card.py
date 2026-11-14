import flet as ft

from services.utils import format_timestamp, format_view_count
from components.importer.import_helpers import MEDIA_TYPES


class ImportItemCard(ft.Container):
    """Apresentação de um item na pré-visualização do importador."""

    def __init__(
        self,
        item,
        index,
        available_tags,
        on_selection,
        on_media_type_change,
        on_remove,
        on_load_metadata=None
    ):
        self.item = item
        self.index = index
        self.available_tags = available_tags
        self.on_load_metadata = on_load_metadata

        super().__init__(
            padding=10,
            border=ft.border.all(
                1,
                ft.Colors.RED_400
                if item["duplicate"]
                else ft.Colors.OUTLINE_VARIANT
            ),
            border_radius=5,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Checkbox(
                        value=item["selected"],
                        disabled=item["duplicate"],
                        on_change=lambda e: on_selection(index, e)
                    ),

                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            ft.Text(
                                item["title"],
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),

                            ft.Text(
                                item["url"],
                                size=11,
                                color=ft.Colors.GREY_400,
                                selectable=True
                            ),

                            ft.Text(
                                item["duplicate_reason"] or "",
                                size=11,
                                color=ft.Colors.RED_400,
                                weight=ft.FontWeight.BOLD,
                                visible=item["duplicate"]
                            ),

                            self.create_metadata_status(),

                            self.create_metadata_preview(),

                            self.create_tag_preview()
                        ]
                    ),

                    self.create_metadata_button(),

                    self.create_media_type_dropdown(
                        on_media_type_change
                    ),

                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Remover da pré-visualização",
                        on_click=lambda e: on_remove(index, e)
                    )
                ]
            )
        )

    # ==================================
    # METADADOS
    # ==================================

    def create_metadata_status(self):

        status = self.item.get(
            "metadata_status",
            "pending"
        )

        status_messages = {
            "pending": ("Metadados não carregados", ft.Colors.GREY_500),
            "loading": ("Carregando informações...", ft.Colors.BLUE_400),
            "loaded": ("Informações carregadas", ft.Colors.GREEN_400),
            "error": ("Falha ao carregar informações", ft.Colors.RED_400)
        }

        message, color = status_messages.get(
            status,
            status_messages["pending"]
        )

        return ft.Text(
            message,
            size=11,
            color=color
        )

    def create_metadata_preview(self):

        if self.item.get("metadata_status") != "loaded":
            return ft.Container(visible=False)

        thumbnail_path = self.item.get("thumbnail_path")

        if thumbnail_path:
            thumbnail = ft.Image(
                src=thumbnail_path,
                width=140,
                height=79,
                fit=ft.ImageFit.COVER
            )
        else:
            thumbnail = ft.Icon(
                ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED,
                size=35,
                color=ft.Colors.GREY_500
            )

        details = []

        uploader = self.item.get("uploader")
        view_count = self.item.get("view_count")
        upload_date = format_timestamp(
            self.item.get("upload_date")
        )
        duration = self.format_duration(
            self.item.get("duration")
        )

        if uploader:
            details.append(f"Canal: {uploader}")

        if view_count is not None:
            details.append(
                f"Visualizações: {format_view_count(view_count)}"
            )

        if upload_date:
            details.append(f"Data: {upload_date}")

        if duration:
            details.append(f"Duração: {duration}")

        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=140,
                    height=79,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=5,
                    content=thumbnail
                ),

                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(
                            detail,
                            size=11,
                            color=ft.Colors.GREY_300
                        )
                        for detail in details
                    ]
                )
            ]
        )

    @staticmethod
    def format_duration(value):

        if value is None:
            return None

        try:
            seconds = int(value)
        except (ValueError, TypeError):
            return str(value)

        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            return f"{hours:02}:{minutes:02}:{seconds:02}"

        return f"{minutes:02}:{seconds:02}"

    def create_metadata_button(self):

        status = self.item.get(
            "metadata_status",
            "pending"
        )

        button_labels = {
            "pending": "Carregar informações",
            "loading": "Carregando...",
            "loaded": "Atualizar",
            "error": "Tentar novamente"
        }

        return ft.OutlinedButton(
            text=button_labels.get(
                status,
                "Carregar informações"
            ),
            icon=(
                ft.Icons.DOWNLOAD
                if status in ("pending", "error")
                else None
            ),
            disabled=(
                self.item["duplicate"]
                or status == "loading"
                or self.on_load_metadata is None
            ),
            on_click=(
                lambda e: self.on_load_metadata(self.index, e)
                if self.on_load_metadata
                else None
            )
        )

    # ==================================
    # TIPO DE MÍDIA
    # ==================================

    def create_media_type_dropdown(self, on_media_type_change):

        return ft.Dropdown(
            width=155,
            dense=True,
            text_size=11,
            value=self.item["media_type"],
            options=[
                ft.dropdown.Option(
                    key=value,
                    text=label
                )
                for value, label in MEDIA_TYPES
            ],
            disabled=self.item["duplicate"],
            on_change=lambda e: on_media_type_change(
                self.index,
                e
            )
        )

    # ==================================
    # TAGS
    # ==================================

    def create_tag_preview(self):

        tags = self.item.get("tags", [])

        if not tags:
            return ft.Text(
                "Sem tags",
                size=11,
                color=ft.Colors.GREY_500
            )

        tags_by_name = {
            tag["name"]: tag
            for tag in self.available_tags
        }

        tag_controls = []

        for tag_name in tags:

            tag = tags_by_name.get(tag_name, {})
            color = tag.get("color") or "#2196F3"

            tag_controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(
                        horizontal=8,
                        vertical=3
                    ),
                    border=ft.border.all(1, color),
                    border_radius=10,
                    content=ft.Text(
                        tag_name,
                        size=10,
                        color=color
                    )
                )
            )

        return ft.Row(
            wrap=True,
            spacing=5,
            run_spacing=5,
            controls=tag_controls
        )
