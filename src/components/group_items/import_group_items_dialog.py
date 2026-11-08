import json
import flet as ft

from urllib.parse import urlparse, parse_qs

from services.db_service import (
    get_all_tags,
    create_group_item
)


MEDIA_TYPES = [
    ("youtube_video", "YouTube Video"),
    ("youtube_shorts", "YouTube Shorts"),
    ("youtube_channel", "YouTube Channel"),
    ("video", "Vídeo"),
    ("image", "Imagem"),
    ("article", "Artigo"),
    ("website", "Website"),
]


class ImportGroupItemsDialog(ft.AlertDialog):

    def __init__(
        self,
        group: dict,
        existing_items=None,
        on_import_complete=None
    ):
        super().__init__()

        self.group = group
        self.existing_items = existing_items or []
        self.on_import_complete = on_import_complete

        self.existing_urls = {
            item.get("url", "").strip()
            for item in self.existing_items
            if item.get("url")
        }

        self.selected_file = None
        self.items = []
        self.skipped_count = 0

        self.available_tags = get_all_tags()

        self.file_picker = ft.FilePicker(
            on_result=self.on_file_selected
        )

        self.file_name = ft.Text(
            "Nenhum arquivo selecionado",
            size=12,
            color=ft.Colors.GREY_400
        )

        self.items_count = ft.Text(
            "Nenhum arquivo carregado.",
            size=13,
            color=ft.Colors.GREY_400
        )

        self.selected_count = ft.Text(
            "0 selecionados",
            size=12,
            color=ft.Colors.GREY_400
        )

        self.select_all = ft.Checkbox(
            label="Selecionar todos",
            value=False,
            on_change=self.on_select_all
        )

        self.preview_list = ft.ListView(
            expand=True,
            spacing=5,
            controls=[]
        )

        self.import_button = ft.OutlinedButton(
            text="Importar",
            icon=ft.Icons.DOWNLOAD,
            disabled=True,
            on_click=self.import_selected_items
        )

        self.modal = True
        self.title = ft.Text("Importar itens para o grupo")

        self.content = ft.Column(
            width=750,
            height=550,
            spacing=10,
            controls=[
                ft.Text(
                    f'Grupo: {group.get("name", "Grupo")}',
                    weight=ft.FontWeight.BOLD
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.OutlinedButton(
                                    text="Selecionar arquivo",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    on_click=self.pick_file
                                ),
                                self.file_name
                            ]
                        ),

                        ft.OutlinedButton(
                            text="Editar Tags",
                            icon=ft.Icons.LABEL,
                            on_click=self.open_bulk_tags_editor
                        )
                    ]
                ),

                ft.Divider(height=5),

                self.items_count,

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.select_all,
                        self.selected_count
                    ]
                ),

                self.preview_list
            ]
        )

        self.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=self.close
            ),
            self.import_button
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

        # Guarda o conteúdo original da janela de importação.
        self.preview_content = self.content
        self.preview_title = self.title
        self.preview_actions = self.actions

    # ---------------------------------------------------------
    # CICLO DE VIDA
    # ---------------------------------------------------------

    def did_mount(self):
        self.page.overlay.append(self.file_picker)
        self.page.update()

    def will_unmount(self):
        if self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)

    # ---------------------------------------------------------
    # ARQUIVO JSON
    # ---------------------------------------------------------

    def pick_file(self, e):
        self.file_picker.pick_files(
            allowed_extensions=["json"],
            allow_multiple=False
        )

    def on_file_selected(self, e: ft.FilePickerResultEvent):

        if not e.files:
            return

        self.selected_file = e.files[0].path

        self.file_name.value = e.files[0].name
        self.file_name.color = ft.Colors.GREEN

        self.load_json()

    def load_json(self):

        try:
            with open(self.selected_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError(
                    "O arquivo precisa conter uma lista de itens."
                )

            self.items = []
            self.skipped_count = 0

            seen_urls = set()

            for item in data:

                if not isinstance(item, dict):
                    self.skipped_count += 1
                    continue

                url = item.get("url")
                title = item.get("title")

                if not isinstance(url, str) or not url.strip():
                    self.skipped_count += 1
                    continue

                url = url.strip()

                if url == "chrome://newtab/":
                    self.skipped_count += 1
                    continue

                if not isinstance(title, str) or not title.strip():
                    title = url

                duplicate_reason = None

                if url in self.existing_urls:
                    duplicate_reason = "Já existe neste grupo"

                elif url in seen_urls:
                    duplicate_reason = "Repetido no arquivo"

                seen_urls.add(url)

                self.items.append({
                    "url": url,
                    "title": title.strip(),
                    "selected": duplicate_reason is None,
                    "duplicate": duplicate_reason is not None,
                    "duplicate_reason": duplicate_reason,
                    "media_type": self.detect_media_type(url),
                    "tags": []
                })

            self.update_preview()

        except (OSError, json.JSONDecodeError, ValueError) as error:

            self.items = []
            self.preview_list.controls = []

            self.items_count.value = f"Erro ao carregar arquivo: {error}"
            self.items_count.color = ft.Colors.RED

            self.select_all.value = False
            self.selected_count.value = "0 selecionados"
            self.import_button.disabled = True

            self.page.update()

    # ---------------------------------------------------------
    # DETECÇÃO DO TIPO DE MÍDIA
    # ---------------------------------------------------------

    def detect_media_type(self, url):

        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower().split(":")[0]
            path = parsed.path.lower()

            youtube_domains = {
                "youtube.com",
                "www.youtube.com",
                "m.youtube.com",
                "music.youtube.com",
                "youtu.be"
            }

            if hostname in youtube_domains:

                if path.startswith("/shorts/"):
                    return "youtube_shorts"

                if hostname == "youtu.be":
                    return "youtube_video"

                if path.startswith("/watch"):
                    return "youtube_video"

                if (
                    path.startswith("/@")
                    or path.startswith("/channel/")
                    or path.startswith("/c/")
                    or path.startswith("/user/")
                ):
                    return "youtube_channel"

            return "website"

        except Exception:
            return "website"

    def extract_media_id(self, url, media_type):

        if media_type not in ("youtube_video", "youtube_shorts"):
            return None

        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower().split(":")[0]

            if hostname == "youtu.be":
                return parsed.path.strip("/").split("/")[0] or None

            query = parse_qs(parsed.query)

            if query.get("v"):
                return query["v"][0]

            path_parts = [
                part for part in parsed.path.split("/")
                if part
            ]

            if len(path_parts) >= 2 and path_parts[0] == "shorts":
                return path_parts[1]

        except Exception:
            pass

        return None

    def create_media_type_dropdown(self, item, index):

        return ft.Dropdown(
            width=155,
            dense=True,
            text_size=11,
            value=item["media_type"],
            options=[
                ft.dropdown.Option(
                    key=value,
                    text=label
                )
                for value, label in MEDIA_TYPES
            ],
            disabled=item["duplicate"],
            on_change=lambda e, i=index: self.on_media_type_change(i, e)
        )

    def on_media_type_change(self, index, e):
        self.items[index]["media_type"] = e.control.value

    # ---------------------------------------------------------
    # TAGS
    # ---------------------------------------------------------

    def create_tag_preview(self, item):

        tags = item.get("tags", [])

        if not tags:
            return ft.Text(
                "Sem tags",
                size=11,
                color=ft.Colors.GREY_500
            )

        tag_controls = []

        tags_by_name = {
            tag["name"]: tag
            for tag in self.available_tags
        }

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

    def open_bulk_tags_editor(self, e):

        checkboxes = []

        for tag in self.available_tags:

            checkbox = ft.Checkbox(
                label=tag["name"],
                value=False
            )

            checkboxes.append((tag, checkbox))

        apply_to_all = ft.Checkbox(
            label="Aplicar alterações para todos os itens importados",
            value=False
        )

        selected_count = sum(
            1 for item in self.items
            if item["selected"] and not item["duplicate"]
        )

        selection_count_text = ft.Text(
            f"{selected_count} itens selecionados",
            size=13,
            color=ft.Colors.GREEN_400
        )

        error_text = ft.Text(
            color=ft.Colors.ERROR,
            size=12
        )

        if not checkboxes:
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
                    for tag, checkbox in checkboxes
                ]
            )

        self.title = ft.Text(
            "Editar Tags dos itens selecionados",
            size=18
        )

        self.content = ft.Container(
            width=400,
            height=390,
            content=ft.Column(
                spacing=12,
                controls=[
                    selection_count_text,
                    ft.Divider(height=5),
                    editor_content,
                    ft.Divider(height=5),
                    apply_to_all,
                    error_text
                ]
            )
        )

        self.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: self.close_bulk_tags_editor()
            ),
            ft.OutlinedButton(
                "Remover",
                icon=ft.Icons.REMOVE,
                style=ft.ButtonStyle(
                    color=ft.Colors.RED_400,
                    padding=ft.padding.symmetric(horizontal=18)
                ),
                on_click=lambda e: self.save_bulk_tags(
                    "remove", apply_to_all, checkboxes, error_text
                )
            ),
            ft.OutlinedButton(
                "Adicionar",
                icon=ft.Icons.ADD,
                style=ft.ButtonStyle(
                    color=ft.Colors.GREEN_400,
                    padding=ft.padding.symmetric(horizontal=18)
                ),
                on_click=lambda e: self.save_bulk_tags(
                    "add", apply_to_all, checkboxes, error_text
                )
            )
        ]

        self.page.update()

    def close_bulk_tags_editor(self):

        self.title = self.preview_title
        self.content = self.preview_content
        self.actions = self.preview_actions

        self.page.update()

    def save_bulk_tags(
        self,
        action,
        apply_to_all,
        checkboxes,
        error_text
    ):

        selected_tags = [
            tag["name"]
            for tag, checkbox in checkboxes
            if checkbox.value
        ]

        if not selected_tags:
            error_text.value = "Selecione pelo menos uma tag."
            self.page.update()
            return

        if apply_to_all.value:

            target_items = [
                item for item in self.items
                if not item["duplicate"]
            ]

        else:

            target_items = [
                item for item in self.items
                if item["selected"] and not item["duplicate"]
            ]

        if not target_items:

            error_text.value = (
                "Nenhum item selecionado. "
                "Marque os itens ou aplique à lista inteira."
            )

            self.page.update()
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

        self.close_bulk_tags_editor()
        self.update_preview()

    # ---------------------------------------------------------
    # IMPORTAÇÃO PARA O GRUPO
    # ---------------------------------------------------------

    def import_selected_items(self, e):

        selected_items = [
            item for item in self.items
            if item["selected"] and not item["duplicate"]
        ]

        if not selected_items:
            self.show_message(
                "Selecione pelo menos um item para importar."
            )
            return

        imported_items = []
        errors = []

        group_id = str(self.group["_id"])

        for item in selected_items:

            item_data = {
                "media_type": item["media_type"],
                "media_id": self.extract_media_id(
                    item["url"],
                    item["media_type"]
                ),
                "url": item["url"],
                "title": item["title"],
                "thumbnail_path": None,
                "text": None,
                "priority": "low",
                "tags": list(item.get("tags", [])),
                "load_status": "json_imported"
            }

            try:
                create_group_item(
                    group_id=group_id,
                    item_data=item_data
                )

                imported_items.append(item)

            except Exception as error:
                errors.append(
                    f'{item["title"]}: {error}'
                )

        # Atualiza a lista local para impedir que itens já gravados
        # sejam enviados novamente em uma nova tentativa.
        for item in imported_items:

            item["selected"] = False
            item["duplicate"] = True
            item["duplicate_reason"] = "Importado nesta operação"

            self.existing_urls.add(item["url"])

        if imported_items and self.on_import_complete:
            self.on_import_complete()

        if errors:

            self.update_preview()

            message = (
                f"{len(imported_items)} importados; "
                f"{len(errors)} não puderam ser importados."
            )

            if imported_items:
                message += " Os itens restantes continuam disponíveis para nova tentativa."

            self.show_message(message)

            print("Erros durante a importação:")
            for error in errors:
                print(error)

            return

        self.page.close(self)

        self.show_message(
            f"{len(imported_items)} itens importados com sucesso!"
        )

    def show_message(self, message):

        self.page.open(
            ft.SnackBar(
                content=ft.Text(message)
            )
        )

    # ---------------------------------------------------------
    # PRÉ-VISUALIZAÇÃO
    # ---------------------------------------------------------

    def update_preview(self):

        total = len(self.items)

        duplicates = sum(
            1 for item in self.items
            if item["duplicate"]
        )

        valid_items = total - duplicates

        self.items_count.value = (
            f"{total} itens encontrados"
            f" | {valid_items} válidos"
            f" | {duplicates} duplicados"
            + (
                f" | {self.skipped_count} ignorados"
                if self.skipped_count else ""
            )
        )

        self.items_count.color = ft.Colors.GREEN

        self.preview_list.controls = [
            ft.Container(
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
                            on_change=lambda e, i=index: self.on_item_selection(i, e)
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

                                self.create_tag_preview(item)
                            ]
                        ),

                        self.create_media_type_dropdown(item, index)
                    ]
                )
            )
            for index, item in enumerate(self.items)
        ]

        self.update_selection()

    def on_item_selection(self, index, e):

        self.items[index]["selected"] = e.control.value

        self.update_selection()

    def on_select_all(self, e):

        selected = e.control.value

        for item in self.items:
            if not item["duplicate"]:
                item["selected"] = selected

        self.update_preview()

    def update_selection(self):

        valid_items = [
            item for item in self.items
            if not item["duplicate"]
        ]

        selected = sum(
            1 for item in valid_items
            if item["selected"]
        )

        total = len(valid_items)

        self.selected_count.value = (
            f"{selected} / {total} selecionados"
        )

        self.select_all.value = (
            total > 0 and selected == total
        )

        self.import_button.disabled = selected == 0

        self.page.update()

    def close(self, e):
        self.page.close(self)
