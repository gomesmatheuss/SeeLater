
from datetime import datetime

from models.tab import Tab
from models.video import Video
from models.enums.priority import Priority
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType
from components.importer.import_helpers import extract_media_id

from services.db_service import (
    create_group_item,
    get_tabs_list,
    get_group_items,
    get_last_index,
    save_tabs,
    save_video
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

        metadata_loaded = (
            item.get("metadata_status") == "loaded"
        )

        content_id = None

        if metadata_loaded:

            content_id = extract_media_id(
                item["url"],
                item["media_type"]
            )

            video = Video(
                id=content_id,
                url=item["url"],
                title=item["title"],
                uploader=item.get("uploader"),
                view_count=item.get("view_count"),
                thumbnail_path=item.get("thumbnail_path"),
                upload_date=item.get("upload_date"),
                duration=item.get("duration"),
                channel_id=item.get("channel_id"),
                channel_thumbnail_path=item.get(
                    "channel_thumbnail_path"
                ),
                last_update=now,
                load_status=LoadStatus.LOAD_SUCCESS,
                media_type=MediaType(item["media_type"]),
                active=True
            )

            save_video(video.to_dict())

        tab = Tab(
            url=item["url"],
            title=item["title"],
            index=index,
            priority=Priority.LOW,
            create_at=now,
            last_update=now,
            tags=list(item.get("tags", [])),
            load_status=(
                LoadStatus.LOAD_SUCCESS
                if metadata_loaded
                else LoadStatus.JSON_IMPORTED
            ),
            content_id=content_id,
            media_type=MediaType(item["media_type"]),
            active=True
        )

        tabs.append(tab.to_dict())

    save_tabs(tabs)

    return len(tabs)

