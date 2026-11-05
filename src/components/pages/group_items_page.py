
import flet as ft

from components.video_card import Card
from components.search_bar import SearchBar
from components.grid_pagination import GridPagination

from services.group_service import GroupService
from services.db_service import set_watched


class GroupItemsPage(ft.Column):

    def __init__(self, page: ft.Page, group: dict, on_back=None):
        super().__init__()

        self.page = page
        self.group = group
        self.on_back = on_back

        self.service = GroupService()

        self.search_term = ""
        self.items_per_page = 54
        self.all_items = []

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN
        self.spacing = 5

        # Cabeçalho
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
                )
            ]
        )

        # Pesquisa
        self.search_bar = SearchBar(
            on_search=self.on_search
        )

        # Cards
        self.cards_row = ft.Row(
            spacing=15,
            run_spacing=15,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # Paginação
        self.pagination_controls = GridPagination(
            on_page_change=self.on_page_change,
            current_page=0,
            total_items=0,
            items_per_page=self.items_per_page
        )

        self.controls = [
            self.header,
            self.search_bar,
            self.cards_row,
            self.pagination_controls
        ]

        self.load_items()

    def go_back(self, e):
        if self.on_back:
            self.on_back()

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

        for video in self.all_items:

            tags = self.service.get_video_tags(video)

            tag_names = [
                tag["name"].lower()
                for tag in tags
            ]

            if (
                search_term in video.title.lower()
                or search_term in video.url.lower()
                or any(search_term in tag for tag in tag_names)
            ):
                filtered_items.append(video)

        return filtered_items

    def on_search(self, query):

        self.search_term = query or ""
        self.pagination_controls.current_page = 0

        self.update_cards()

    def on_page_change(self, page):
        self.update_cards()

    def update_cards(self):

        filtered_items = self.get_filtered_items()

        current_page = self.pagination_controls.current_page

        start = current_page * self.items_per_page
        end = start + self.items_per_page

        page_items = filtered_items[start:end]

        self.cards_row.controls = [
            Card(
                video,
                self.page,
                self.on_card_changed,
                tags=self.service.get_video_tags(video)
            )
            for video in page_items
        ]

        if not filtered_items:
            self.cards_row.controls = [
                ft.Container(
                    padding=30,
                    content=ft.Text(
                        "Nenhum vídeo encontrado neste grupo.",
                        color=ft.Colors.GREY_400
                    )
                )
            ]

        self.pagination_controls.set_data(
            current_page=current_page,
            total_items=len(filtered_items)
        )

        self.page.update()

    def on_card_changed(self, video):

        set_watched(video.id)

        self.service.invalidate_cache()

        self.load_items(hard_refresh=True)
