
import flet as ft

from components.media_collection import MediaCollection
from components.media_card_assembler import MediaCardAssembler

from services.grid_service import GridService
from services.video_queue_service import get_video_queue


class Grid(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()

        # Referência permanente à página principal.
        self.app_page = page

        self.search_term = ""
        self.items_per_page = 54

        self.service = GridService()

        # Instância compartilhada da fila.
        self.video_queue = get_video_queue()

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.collection = MediaCollection(
            on_page_change=self.on_page_change,
            card_builder=self.create_card,
            items_per_page=self.items_per_page,
            empty_message="Nenhum vídeo encontrado."
        )

        self.controls = [
            self.collection
        ]

        self.update_cards()

    # ==================================
    # CRIAÇÃO DOS CARDS
    # ==================================

    def create_card(self, video):

        return MediaCardAssembler.create_card(
            item=video,
            page=self.app_page,
            tags=self.service.get_video_tags(video)
        )

    # ==================================
    # ATUALIZAÇÃO DOS CARDS
    # ==================================

    def on_page_change(self, page):
        self.update_cards(
            change_page=True
        )

    def update_cards(
        self,
        search_term="",
        change_page=False,
        hard_refresh=False
    ):

        if not change_page:
            self.search_term = search_term
            self.collection.pagination.current_page = 0

        current_page = self.collection.pagination.current_page

        videos = self.service.get_page_videos(
            current_page=current_page,
            items_per_page=self.items_per_page,
            search_term=self.search_term,
            hard_refresh=hard_refresh
        )

        total_items = self.service.get_total_items(
            self.search_term
        )

        self.collection.set_items(
            items=videos,
            total_items=total_items,
            current_page=current_page
        )

        # Solicita o carregamento dos vídeos pendentes.
        self.enqueue_pending_videos(videos)

        self.app_page.update()

    # ==================================
    # FILA DE CARREGAMENTO
    # ==================================

    def enqueue_pending_videos(self, videos):

        pending_tabs = self.service.get_pending_tabs(
            videos
        )

        for tab in pending_tabs:

            try:
                self.video_queue.enqueue(
                    tab,
                    on_complete=self.on_video_load_complete
                )

            except Exception as e:

                print(
                    f"Erro ao adicionar vídeo à fila: {e}"
                )

    def on_video_load_complete(
        self,
        video_id,
        video,
        error
    ):

        # Em caso de falha, não atualiza a página
        # automaticamente, evitando novas tentativas
        # consecutivas sem intervenção.
        if error is not None:
            return

        try:
            self.app_page.run_task(
                self.refresh_after_video_load
            )

        except Exception as e:

            print(
                "Erro ao agendar atualização da Home:",
                e
            )

    async def refresh_after_video_load(self):

        self.update_cards(
            change_page=True,
            hard_refresh=True
        )
