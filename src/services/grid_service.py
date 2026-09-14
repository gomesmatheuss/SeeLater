from services.video_service import load_card_info
from services.db_service import get_tabs_list, get_all_videos


class GridService:

    def __init__(self):
        self.all_tabs = []
        self.all_videos = {}

    def load_data(self, hard_refresh=False):
        """
        Carrega os dados utilizados pelo Grid.

        Os dados ficam em memória para evitar consultas
        desnecessárias ao banco durante a navegação.
        """

        if hard_refresh or not self.all_tabs:
            self.all_tabs = get_tabs_list()
            self.all_videos = get_all_videos()

    def get_filtered_tabs(self, search_term=""):
        """
        Retorna os Tabs que correspondem ao termo de pesquisa.
        """

        search_term = search_term.lower()

        return [
            tab
            for tab in self.all_tabs
            if (
                search_term in tab["title"].lower()
                or search_term in tab["url"].lower()
                or search_term in tab["tags"]
            )
        ]

    def get_page_tabs(
        self,
        current_page,
        items_per_page,
        search_term="",
        hard_refresh=False
    ):
        """
        Retorna somente os Tabs pertencentes à página atual.
        """

        self.load_data(hard_refresh)

        tabs = self.get_filtered_tabs(search_term)

        start = current_page * items_per_page
        end = start + items_per_page

        return tabs[start:end]

    def get_page_videos(
        self,
        current_page,
        items_per_page,
        search_term="",
        hard_refresh=False
    ):
        """
        Retorna os Videos da página atual.
        """

        tabs = self.get_page_tabs(
            current_page=current_page,
            items_per_page=items_per_page,
            search_term=search_term,
            hard_refresh=hard_refresh
        )

        videos = []

        for tab in tabs:
            video = load_card_info(
                tab,
                self.all_videos
            )

            if video:
                videos.append(video)

        return videos

    def get_total_items(self, search_term=""):
        """
        Retorna a quantidade total de Tabs encontrados
        pela pesquisa atual.
        """

        return len(
            self.get_filtered_tabs(search_term)
        )
