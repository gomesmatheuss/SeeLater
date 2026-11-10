
from datetime import datetime

from models.tab import Tab
from models.enums.priority import Priority
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType

from services.db_service import (
    create_group_item,
    get_tabs_list,
    get_group_items,
    get_last_index,
    save_tabs
)


def get_existing_items(destination, group_id=None):

    if destination == "group":

        if not group_id:
            return []

        return get_group_items(group_id)

    return get_tabs_list()


def save_imported_group_item(group_id, item_data):

    return create_group_item(
        group_id=group_id,
        item_data=item_data
    )


def save_imported_home_items(items):

    if not items:
        return 0

    now = datetime.now()
    index = get_last_index()

    tabs = []

    for item in items:

        index += 10

        tab = Tab(
            url=item["url"],
            title=item["title"],
            index=index,
            priority=Priority.LOW,
            create_at=now,
            last_update=now,
            tags=list(item.get("tags", [])),
            load_status=LoadStatus.JSON_IMPORTED,
            content_id=None,
            media_type=MediaType(item["media_type"]),
            active=True
        )

        tabs.append(tab.to_dict())

    save_tabs(tabs)

    return len(tabs)
