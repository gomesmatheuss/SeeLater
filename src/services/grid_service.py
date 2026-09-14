from services.video_service import load_card_info
from services.db_service import get_tabs_list, get_all_videos


class GridService:

    def __init__(self):
        self.all_tabs = []
        self.all_videos = {}

        # Cache dos resultados processados.
        # A chave é o termo de pesquisa.
        self.video_cache = {}

    def load_data(self, hard_refresh=False):
        """
        Carrega os dados utilizados pelo Grid.

        Os dados ficam em memória para evitar consultas
        desnecessárias ao banco durante a navegação.
        """

        if hard_refresh or not self.all_tabs:
            self.all_tabs = get_tabs_list()
            self.all_videos = get_all_videos()

            # Como os dados foram atualizados, os resultados
            # antigos do cache deixam de ser válidos.
            self.video_cache.clear()

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

    def get_valid_videos(self, search_term=""):
        """
        Retorna os Videos válidos para o termo de pesquisa.

        O resultado é armazenado em cache para que a conversão
        dos Tabs em Videos aconteça apenas uma vez por pesquisa.
        """

        search_term = search_term.lower()

        # Se já processamos essa pesquisa, reutilizamos o resultado.
        if search_term in self.video_cache:
            return self.video_cache[search_term]

        tabs = self.get_filtered_tabs(search_term)

        videos = []

        for tab in tabs:
            video = load_card_info(
                tab,
                self.all_videos
            )

            if video:
                videos.append(video)

        self.video_cache[search_term] = videos

        return videos

    def get_page_videos(
        self,
        current_page,
        items_per_page,
        search_term="",
        hard_refresh=False
    ):
        """
        Retorna somente os Videos válidos pertencentes
        à página atual.
        """

        self.load_data(hard_refresh)

        videos = self.get_valid_videos(search_term)

        start = current_page * items_per_page
        end = start + items_per_page

        return videos[start:end]

    def get_total_items(self, search_term=""):
        """
        Retorna a quantidade de Videos válidos encontrados
        pela pesquisa atual.
        """

        self.load_data()

        videos = self.get_valid_videos(search_term)

        return len(videos)
