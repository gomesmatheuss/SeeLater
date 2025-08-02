import flet as ft
from components.video_card import Card
from services.video_service import get_video_info, get_not_loaded_video_info
from services.db_service import get_tabs_list
from services.add_video_dialog import open_video_dialog
from models.enums.load_status import LoadStatus

class FABButton(ft.FloatingActionButton):
    def __init__(self, page: ft.Page, grid):
        super().__init__()
        self.page = page
        self.grid = grid
        self.icon = ft.Icons.ADD
        self.bgcolor = ft.Colors.BLUE
        self.tooltip = "Adicionar novo vídeo"
        self.on_click = self.on_click_handler

    def on_click_handler(self, e):
        def after_dialog(result):
            self.grid.refresh()

        open_video_dialog(self.page, callback=after_dialog)
        
        
class Grid(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.floating_action_button = FABButton(self.page, self)

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN
        self.controls = [
            ft.Row(
                spacing = 15,
                run_spacing = 15,
                wrap = True,
                vertical_alignment = ft.CrossAxisAlignment.START,
                controls = self.create_cards()
            )
        ]

    def create_cards(self, search_query=""):
        tabs = get_tabs_list()
        cards = []
        for tab in tabs:
            if search_query.lower() not in tab["title"].lower() and \
               search_query.lower() not in tab["url"].lower():
                continue

            if "youtube" in tab["url"]:
                if tab.get("load_status") and (LoadStatus(tab.get("load_status")) == LoadStatus.JSON_IMPORTED):
                    video = get_not_loaded_video_info(tab)
                    cards.append(Card(video))
                else:
                    video = get_video_info(tab)
                    if video:
                        cards.append(Card(video))
        return cards

    def refresh(self, query):
        new_cards = self.create_cards(query)
        self.controls[0].controls = new_cards
        self.update()
