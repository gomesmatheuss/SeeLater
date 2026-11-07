
import flet as ft

from components.video_card import Card
from components.fab_button import FABButton
from components.grid_pagination import GridPagination

from services.grid_service import GridService
from services.video_queue_service import get_video_queue


class Grid(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.search_term = ""
        self.items_per_page = 54

        self.service = GridService()

        # Instância compartilhada da fila.
        self.video_queue = get_video_queue()

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.page.floating_action_button = FABButton(
            self.page,
            self.on_video_added
        )

        self.cards_row = ft.Row(
            spacing=15,
            run_spacing=15,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.pagination_controls = GridPagination(
            on_page_change=self.on_page_change,
            current_page=0,
            total_items=0,
            items_per_page=self.items_per_page
        )

        self.controls = [
            self.cards_row,
            self.pagination_controls
        ]

        self.update_cards()

    # ==================================
    # ATUALIZAÇÃO DOS CARDS
    # ==================================

    def on_video_added(self):
        self.update_cards(
            hard_refresh=True
        )

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
            self.pagination_controls.current_page = 0

        current_page = self.pagination_controls.current_page

        videos = self.service.get_page_videos(
            current_page=current_page,
            items_per_page=self.items_per_page,
            search_term=self.search_term,
            hard_refresh=hard_refresh
        )

        cards = [
            Card(
                video,
                self.page,
                self.on_card_changed,
                tags=self.service.get_video_tags(video)
            )
            for video in videos
        ]

        self.cards_row.controls = cards

        total_items = self.service.get_total_items(
            self.search_term
        )

        self.pagination_controls.set_data(
            current_page=current_page,
            total_items=total_items
        )

        # Solicita o carregamento dos vídeos pendentes.
        self.enqueue_pending_videos(videos)

        self.page.update()

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
            # Encaminha a atualização para o loop
            # de execução da página Flet.
            self.page.run_task(
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

    # ==================================
    # ALTERAÇÕES NOS CARDS
    # ==================================

    def on_card_changed(self, video):
        """
        Chamado quando um Card altera alguma informação.
        """

        self.service.mark_as_watched(video)

        self.update_cards(
            hard_refresh=True
        )
