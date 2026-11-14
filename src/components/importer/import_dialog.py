import json
import flet as ft

from urllib.parse import urlparse

from components.importer.import_preview import ImportPreview
from components.importer.bulk_tags_dialog import BulkTagsDialog
from components.importer.import_helpers import (
    detect_media_type,
    extract_media_id
)
from services.db_service import get_all_tags
from services.import_service import (
    save_imported_group_item,
    save_imported_home_items,
    get_existing_items
)
from services.video_queue_service import get_video_queue


class ImportItemsDialog(ft.AlertDialog):

    def __init__(
        self,
        group=None,
        existing_items=None,
        on_import_complete=None
    ):
        super().__init__()

        window_height = self.page.window.height if self.page else 720

        dialog_height = max(
            400,
            min(750, window_height * 0.75)
        )

        self.group = group
        self.destination = "group" if group else "home"

        self.existing_items = get_existing_items(
            destination=self.destination,
            group_id=str(group["_id"]) if group else None
        )
        self.on_import_complete = on_import_complete
        self.video_queue = get_video_queue()
        self.metadata_requests = {}
        self.dialog_closed = False
        self.close_confirmation = False

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

        self.manual_url_input = ft.TextField(
            label="Adicionar URL",
            hint_text="Cole uma URL aqui...",
            expand=True,
            on_submit=self.add_manual_url
        )

        self.items_count = ft.Text(
            "Nenhum arquivo carregado.",
            size=13,
            color=ft.Colors.GREY_400,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            text_align=ft.TextAlign.CENTER
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

        self.preview_list = ImportPreview(
            available_tags=self.available_tags,
            on_selection=self.on_item_selection,
            on_media_type_change=self.on_media_type_change,
            on_remove=self.remove_item,
            on_load_metadata=self.load_item_metadata
        )

        self.import_button = ft.OutlinedButton(
            text="Importar",
            icon=ft.Icons.DOWNLOAD,
            disabled=True,
            on_click=self.import_selected_items
        )

        self.modal = True
        self.title = ft.Text(
            "Importar itens para o grupo"
            if self.destination == "group"
            else "Importar itens"
        )

        self.content = ft.Column(
            width=750,
            height=dialog_height,
            spacing=10,
            controls=[
                ft.Text(
                    f'Grupo: {group.get("name", "Grupo")}',
                    weight=ft.FontWeight.BOLD
                ) if self.destination == "group" else ft.Container(),

                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.manual_url_input,
                        ft.OutlinedButton(
                            text="Adicionar",
                            icon=ft.Icons.ADD,
                            on_click=self.add_manual_url
                        ),
                        ft.OutlinedButton(
                            text="Selecionar arquivo",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=self.pick_file
                        )
                    ]
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.file_name,

                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.OutlinedButton(
                                    text="Remover selecionados",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=self.remove_selected_items
                                ),
                                ft.OutlinedButton(
                                    text="Editar Tags",
                                    icon=ft.Icons.LABEL,
                                    on_click=self.open_bulk_tags_editor
                                )
                            ]
                        )
                    ]
                ),

                ft.Divider(height=5),

                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.select_all,

                        ft.Container(
                            content=self.items_count,
                            expand=True,
                            alignment=ft.alignment.center
                        ),

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
        self.bulk_tags_dialog = BulkTagsDialog(self)

    # ---------------------------------------------------------
    # CICLO DE VIDA
    # ---------------------------------------------------------

    def did_mount(self):
        self.page.overlay.append(self.file_picker)
        self.page.update()

    def will_unmount(self):

        self.dialog_closed = True
        self._cancel_all_metadata_requests()

        if self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)

    # ---------------------------------------------------------
    # ADIÇÃO MANUAL DE URL
    # ---------------------------------------------------------

    def add_manual_url(self, e=None):

        url = (self.manual_url_input.value or "").strip()

        if not url:
            self.show_message("Informe uma URL para adicionar.")
            return

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            self.show_message("Informe uma URL válida, começando com http:// ou https://.")
            return

        duplicate_reason = None

        if url in self.existing_urls:
            duplicate_reason = "Já existe no destino"

        elif any(item["url"] == url for item in self.items):
            duplicate_reason = "Repetido na pré-visualização"

        self.items.append({
            "url": url,
            "title": url,
            "selected": duplicate_reason is None,
            "duplicate": duplicate_reason is not None,
            "duplicate_reason": duplicate_reason,
            "media_type": detect_media_type(url),
            "tags": []
        })

        self.manual_url_input.value = ""
        self.update_preview()

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

            seen_urls = {
                item["url"] for item in self.items
            }

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
                    duplicate_reason = "Já existe no destino"

                elif url in seen_urls:
                    duplicate_reason = "Repetido na pré-visualização"

                seen_urls.add(url)

                self.items.append({
                    "url": url,
                    "title": title.strip(),
                    "selected": duplicate_reason is None,
                    "duplicate": duplicate_reason is not None,
                    "duplicate_reason": duplicate_reason,
                    "media_type": detect_media_type(url),
                    "tags": []
                })

            self.update_preview()

        except (OSError, json.JSONDecodeError, ValueError) as error:

            self.items_count.value = f"Erro ao carregar arquivo: {error}"
            self.items_count.color = ft.Colors.RED

            self.update_preview()
            self.page.update()

    
    # ---------------------------------------------------------
    # CARREGAMENTO DE METADADOS
    # ---------------------------------------------------------

    def load_item_metadata(self, index, e=None):

        if self.dialog_closed:
            return

        if index < 0 or index >= len(self.items):
            return

        item = self.items[index]

        if item["duplicate"]:
            return

        if item.get("metadata_status") == "loading":
            return

        item["metadata_status"] = "loading"
        item.pop("metadata_error", None)

        video_id = extract_media_id(
            item["url"],
            "youtube_video"
        )

        if not video_id:
            item["metadata_status"] = "error"
            item["metadata_error"] = "URL de vídeo não reconhecida."
            self.update_preview()
            return

        def metadata_callback(video_id, video, error):
            if self.page and not self.dialog_closed:
                self.page.run_thread(
                    self.on_metadata_loaded,
                    item,
                    video,
                    error
                )

        # Registra antes de enfileirar para evitar uma corrida
        # caso a tarefa termine muito rapidamente.
        self.metadata_requests[id(item)] = {
            "video_id": video_id,
            "callback": metadata_callback
        }

        self.update_preview()

        try:
            self.video_queue.enqueue_priority(
                {
                    "url": item["url"],
                    "title": item["title"]
                },
                on_complete=metadata_callback
            )

        except Exception as error:

            self.metadata_requests.pop(id(item), None)

            item["metadata_status"] = "error"
            item["metadata_error"] = str(error)

            print("Erro ao solicitar metadados:", error)

            self.update_preview()

    def on_metadata_loaded(self, item, video, error):

        self.metadata_requests.pop(id(item), None)

        if self.dialog_closed:
            return

        # O item pode ter sido removido enquanto carregava.
        if not any(current is item for current in self.items):
            return

        if error or video is None:

            item["metadata_status"] = "error"
            item["metadata_error"] = str(
                error or "Não foi possível carregar os metadados."
            )

            print(
                f"Falha ao carregar metadados de {item['url']}:",
                item["metadata_error"]
            )

        else:

            item["title"] = video.title
            item["thumbnail_path"] = video.thumbnail_path
            item["uploader"] = video.uploader
            item["view_count"] = video.view_count
            item["upload_date"] = video.upload_date
            item["duration"] = video.duration
            item["channel_id"] = video.channel_id
            item["channel_thumbnail_path"] = (
                video.channel_thumbnail_path
            )

            item["metadata_status"] = "loaded"
            item.pop("metadata_error", None)

        self.update_preview()

    def _cancel_item_metadata(self, item):

        request = self.metadata_requests.pop(id(item), None)

        if not request:
            return

        self.video_queue.remove_priority_callback(
            request["video_id"],
            request["callback"]
        )


    # ---------------------------------------------------------
    # TAGS
    # ---------------------------------------------------------

    def open_bulk_tags_editor(self, e):
        self.bulk_tags_dialog.open(e)

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

        # ==================================
        # IMPORTAÇÃO PARA A HOME
        # ==================================

        if self.destination == "home":

            try:
                imported_count = save_imported_home_items(
                    selected_items
                )

                imported_items = selected_items.copy()

            except Exception as error:
                imported_count = 0
                errors.append(str(error))

        # ==================================
        # IMPORTAÇÃO PARA UM GRUPO
        # ==================================

        else:

            group_id = str(self.group["_id"])

            for item in selected_items:

                item_data = {
                    "media_type": item["media_type"],
                    "media_id": extract_media_id(
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
                    save_imported_group_item(
                        group_id=group_id,
                        item_data=item_data
                    )

                    imported_items.append(item)

                except Exception as error:
                    errors.append(
                        f'{item["title"]}: {error}'
                    )

            imported_count = len(imported_items)

        # ==================================
        # ATUALIZAÇÃO DA PRÉ-VISUALIZAÇÃO
        # ==================================

        for item in imported_items:

            item["selected"] = False
            item["duplicate"] = True
            item["duplicate_reason"] = "Importado nesta operação"

            self.existing_urls.add(item["url"])

        if imported_items and self.on_import_complete:
            self.on_import_complete()

        # ==================================
        # RESULTADO
        # ==================================

        if errors:

            self.update_preview()

            message = (
                f"{imported_count} importados; "
                f"{len(errors)} não puderam ser importados."
            )

            if imported_items:
                message += (
                    " Os itens restantes continuam disponíveis "
                    "para nova tentativa."
                )

            self.show_message(message)

            print("Erros durante a importação:")
            for error in errors:
                print(error)

            return

        self._finish_close()

        self.show_message(
            f"{imported_count} itens importados com sucesso!"
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

        self.preview_list.set_items(self.items)

        self.update_selection()

    def on_media_type_change(self, index, e):
        self.items[index]["media_type"] = e.control.value

    def remove_item(self, index, e=None):

        if index < 0 or index >= len(self.items):
            return

        item = self.items[index]

        self._cancel_item_metadata(item)

        self.items.pop(index)
        self.update_preview()

    def remove_selected_items(self, e=None):

        selected_count = sum(
            1 for item in self.items
            if item["selected"] and not item["duplicate"]
        )

        if selected_count == 0:
            self.show_message("Selecione pelo menos um item para remover.")
            return

        remaining_items = []

        for item in self.items:

            if item["selected"] and not item["duplicate"]:
                self._cancel_item_metadata(item)
            else:
                remaining_items.append(item)

        self.items = remaining_items

        self.update_preview()
        self.show_message(
            f"{selected_count} itens removidos da pré-visualização."
        )

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

    
    # ---------------------------------------------------------
    # FECHAMENTO E CANCELAMENTO
    # ---------------------------------------------------------

    def close(self, e=None):

        if self.dialog_closed:
            return

        if not self.metadata_requests:
            self._finish_close()
            return

        if self.close_confirmation:
            return

        self.close_confirmation = True

        self.title = ft.Text("Carregamentos em andamento")

        self.content = ft.Text(
            "Existem solicitações de metadados em andamento. "
            "Deseja fechar o importador e cancelar essas solicitações?"
        )

        self.actions = [
            ft.TextButton(
                "Continuar importando",
                on_click=self.cancel_close
            ),
            ft.TextButton(
                "Fechar e cancelar",
                on_click=self.confirm_close
            )
        ]

        self.update()

    def cancel_close(self, e=None):

        if not self.close_confirmation:
            return

        self.close_confirmation = False

        self.title = self.preview_title
        self.content = self.preview_content
        self.actions = self.preview_actions

        self.update()

    def confirm_close(self, e=None):

        self.close_confirmation = False
        self._finish_close()

    def _cancel_all_metadata_requests(self):

        requests = list(self.metadata_requests.values())

        self.metadata_requests.clear()

        for request in requests:

            self.video_queue.remove_priority_callback(
                request["video_id"],
                request["callback"]
            )

    def _finish_close(self):

        if self.dialog_closed:
            return

        self.dialog_closed = True

        self._cancel_all_metadata_requests()

        self.page.close(self)
