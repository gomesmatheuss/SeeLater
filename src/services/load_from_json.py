import json
from models.tab import Tab
from services.db_service import save_tabs
from datetime import datetime

def process_json(path):
    with open(path, "r", encoding="utf-8") as f:
        tabs = json.load(f)

    tabs_list = []
    for tab in tabs:
        if tab.get("url") == "chrome://newtab/":
            continue

        tabs_list.append(
            Tab(
                url = tab["url"],
                title = tab["title"],
                index = 0,
                priority = "Baixa",
                create_at = datetime.now()
            ).to_dict()
        )

    save_tabs(tabs_list)