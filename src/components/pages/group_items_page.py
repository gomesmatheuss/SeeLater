
import flet as ft

from components.media_card_assembler import MediaCardAssembler
from components.media_collection import MediaCollection
from components.search_bar import SearchBar

from services.group_service import GroupService
from services.video_queue_service import get_video_queue

from components.importer.import_dialog import ImportItemsDialog


class GroupItemsPage(ft.Column):

    def __init__(self, page: ft.Page, group: dict, on_back=None):
        super().__init__()

        self.page = page
        self.app_page = page
        self.group = group
        self.on_back = on_back

        self.service = GroupService()
        self.video_queue = get_video_queue()

        self.search_term = ""
        self.items_per_page = 54
        self.all_items = []

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN
        self.spacing = 5

        self.header = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Voltar para grupos",
                    on_click=self.go_back
                ),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(
                            group.get("name", "Grupo"),
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            group.get("description", ""),
                            size=12,
                            color=ft.Colors.GREY_400,
                            visible=bool(group.get("description"))
                        )
                    ]
                ),
                ft.ElevatedButton(
                    "Importar itens",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=self.open_import_dialog
                )
            ]
        )

        self.search_bar = SearchBar(
            on_search=self.on_search
        )

        self.collection = MediaCollection(
            on_page_change=self.on_page_change,
            card_builder=self.create_card,
            items_per_page=self.items_per_page,
            empty_message="Nenhum item encontrado neste grupo."
        )

        self.controls = [
            self.header,
            self.search_bar,
            self.collection
        ]

        self.load_items()

    # ==================================
    # NAVEGAÇÃO
    # ==================================

    def go_back(self, e):
        if self.on_back:
            self.on_back()

    # ==================================
    # CARDS
    # ==================================

    def create_card(self, item):

        return MediaCardAssembler.create_card(
            item=item,
            page=self.page,
            tags=self.service.get_item_tags(item)
        )

    # ==================================
    # CARREGAMENTO DOS ITENS
    # ==================================

    def load_items(self, hard_refresh=False):

        self.all_items = self.service.get_group_items(
            group_id=str(self.group["_id"]),
            hard_refresh=hard_refresh
        )

        self.update_cards()

    def get_filtered_items(self):

        search_term = self.search_term.lower().strip()

        if not search_term:
            return self.all_items

        filtered_items = []

        for item in self.all_items:

            tags = self.service.get_item_tags(item)

            tag_names = [
                tag["name"].lower()
                for tag in tags
            ]

            title = item.get("title", "").lower()
            url = item.get("url", "").lower()

            if (
                search_term in title
                or search_term in url
                or any(search_term in tag for tag in tag_names)
            ):
                filtered_items.append(item)

        return filtered_items

    # ==================================
    # FILA DE CARREGAMENTO
    # ==================================

    def enqueue_pending_items(self, items):
        pending_items = self.service.get_pending_items(items)

        for item in pending_items:
            try:
                self.video_queue.enqueue(
                    item,
                    on_complete=self.on_video_load_complete
                )
            except ValueError as e:
                print(
                    f"Item ignorado na fila: "
                    f"{item.get('title') or 'Sem título'} | "
                    f"URL: {item.get('url')} | "
                    f"Motivo: {e}"
                )

    def on_video_load_complete(self, video_id, video, error):

        if error:
            return

        # Não atualiza uma tela que não está mais montada.
        if self.page is None:
            return

        try:
            self.app_page.run_task(
                self.refresh_after_video_load
            )

        except Exception as e:
            print(f"Erro ao atualizar grupo após carregamento: {e}")

    async def refresh_after_video_load(self):

        # A tela pode ter sido desmontada após o agendamento.
        if self.page is None:
            return

        self.load_items(hard_refresh=True)

    # ==================================
    # BUSCA E PAGINAÇÃO
    # ==================================

    def on_search(self, query):

        self.search_term = query or ""
        self.collection.pagination.current_page = 0

        self.update_cards()

    def on_page_change(self, page):
        self.update_cards()

    # ==================================
    # ATUALIZAÇÃO DA COLEÇÃO
    # ==================================

    def update_cards(self):

        filtered_items = self.get_filtered_items()

        current_page = self.collection.pagination.current_page

        start = current_page * self.items_per_page
        end = start + self.items_per_page

        page_items = filtered_items[start:end]

        self.collection.set_items(
            items=page_items,
            total_items=len(filtered_items),
            current_page=current_page
        )

        self.enqueue_pending_items(page_items)

        self.page.update()

    # ==================================
    # IMPORTAÇÃO
    # ==================================

    def open_import_dialog(self, e):

        existing_items = self.service.get_group_items(
            group_id=str(self.group["_id"])
        )

        dialog = ImportItemsDialog(
            group=self.group,
            existing_items=existing_items,
            on_import_complete=lambda: self.load_items(hard_refresh=True)
        )

        self.page.open(dialog)
