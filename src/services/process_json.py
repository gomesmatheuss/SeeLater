import json
from models.tab import Tab
from models.enums.priority import Priority
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType
from services.db_service import save_tabs, get_last_index
from datetime import datetime

def extract_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        itens = json.load(f)

    tabs = []
    itens_count = len(itens)
    tabs_count = 0
    index = get_last_index()

    for tab in itens:
        if tab.get("url") == "chrome://newtab/":
            continue

        index += 10
        tabs_count += 1
        tabs.append(
            Tab(
                url = tab["url"],
                title = tab["title"],
                index = index,
                priority = Priority.LOW,
                create_at = datetime.now(),
                last_update = datetime.now(),
                load_status = LoadStatus.JSON_IMPORTED,
                media_type = MediaType.YOUTUBE_VIDEO
            )
        )

    return tabs, itens_count, tabs_count
