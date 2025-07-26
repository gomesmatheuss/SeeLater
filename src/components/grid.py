import flet as ft
from components.video_card import Card
from services.video_service import get_video_info, get_not_loaded_video_info
from services.db_service import get_tabs_list
from services.add_video_dialog import open_video_dialog

class FABButton(ft.FloatingActionButton):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.icon = ft.Icons.ADD
        self.bgcolor = ft.Colors.BLUE
        self.on_click = lambda x: open_video_dialog(self.page)
        self.tooltip = "Adicionar novo vídeo"
        
        
class Grid(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.floating_action_button = FABButton(self.page)

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

    def create_cards(self):
        tabs = get_tabs_list()
        cards = []
        for tab in tabs:
            if "youtube" in tab["url"]:
                # if not tab.get("load_status") or (tab.get("load_status", "") == "Carregado Por Json"):
                if tab.get("load_status", "") == "Carregado Por Json": #Alterar essa validação quando tiver os status corretos no mongo
                    video = get_not_loaded_video_info(tab)
                    cards.append(Card(video))
                else:
                    video = get_video_info(tab)
                    if video:
                        cards.append(Card(video))


        return cards
