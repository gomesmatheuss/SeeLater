
from services.video_service import load_card_info
from services.db_service import (
    get_tabs_list,
    get_all_videos,
    get_all_tags,
    set_watched
)
from models.enums.load_status import LoadStatus


class GridService:

    def __init__(self):
        self.all_tabs = []
        self.all_videos = {}
        self.all_tags = []

        self.tabs_by_url = {}

        # Cache dos resultados processados.
        # A chave é o termo de pesquisa.
        self.video_cache = {}

    def load_data(self, hard_refresh=False):
        """
        Carrega os dados utilizados pelo Grid.
        """

        if hard_refresh or not self.all_tabs:
            self.all_tabs = get_tabs_list()
            self.all_videos = get_all_videos()
            self.all_tags = get_all_tags()

            # Indexa os Tabs pela URL.
            self.tabs_by_url = {
                tab["url"]: tab
                for tab in self.all_tabs
            }

            # Invalida os resultados antigos.
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
        """

        search_term = search_term.lower()

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

    def get_video_tags(self, video):
        """
        Retorna as tags associadas ao vídeo,
        incluindo suas respectivas cores.
        """

        tab = self.tabs_by_url.get(video.url)

        if not tab:
            return []

        tags_by_name = {
            tag["name"]: tag
            for tag in self.all_tags
        }

        return [
            {
                "name": tag_name,
                "color": tags_by_name[tag_name].get(
                    "color",
                    "#2196F3"
                )
            }
            for tag_name in tab.get("tags", [])
            if tag_name in tags_by_name
        ]

    def get_page_videos(
        self,
        current_page,
        items_per_page,
        search_term="",
        hard_refresh=False
    ):
        """
        Retorna somente os Videos pertencentes
        à página atual.
        """

        self.load_data(hard_refresh)

        videos = self.get_valid_videos(search_term)

        start = current_page * items_per_page
        end = start + items_per_page

        return videos[start:end]

    def get_total_items(self, search_term=""):
        """
        Retorna a quantidade de Videos encontrados.
        """

        self.load_data()

        videos = self.get_valid_videos(search_term)

        return len(videos)

    def mark_as_watched(self, video):
        """
        Marca o vídeo como visto no banco de dados.
        """

        set_watched(video.id)

        self.video_cache.clear()

    def get_pending_tabs(self, videos):
        """
        Retorna somente os Tabs que ainda não foram
        carregados e estão aguardando processamento.
        """

        pending_tabs = []

        pending_statuses = {
            LoadStatus.JSON_IMPORTED,
            LoadStatus.READY_FOR_LOAD
        }

        for video in videos:

            tab = self.tabs_by_url.get(video.url)

            if not tab:
                continue

            status = tab.get(
                "load_status",
                LoadStatus.LOAD_FAILED
            )

            # Compatibilidade com registros antigos.
            if type(status) == int:
                status = LoadStatus.LOAD_FAILED

            try:
                status = LoadStatus(status)

            except (ValueError, TypeError):
                continue

            if status in pending_statuses:
                pending_tabs.append(tab)

        return pending_tabs
