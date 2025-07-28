from datetime import datetime
from dataclasses import dataclass
from typing import List
from models.enums.priority import Priority
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType

@dataclass
class Tab:
    url: str
    title: str
    index: int
    priority: Priority
    create_at: datetime
    last_update: datetime = None
    tags: List[str] = None
    load_status: LoadStatus = None
    content_id: str = None
    media_type: MediaType = None
    active: bool = True

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "index": self.index,
            "priority": self.priority.value,
            "create_at": self.create_at,
            "last_update": self.last_update,
            "tags": self.tags,
            "load_status": self.load_status.value,
            "content_id": self.content_id,
            "media_type": self.media_type.value,
            "active": self.active
        }
    
    @staticmethod
    def from_dict(tab: dict):
        Tab(
            url = tab.get("url", ""),
            title = tab.get("title", ""),
            index = tab.get("index", 0),
            priority = Priority(tab.get("priority")),
            create_at = tab.get("create_at"),
            last_update = tab.get("last_update"),
            tags = tab.get("tags", []),
            load_status = LoadStatus(tab.get("load_status")),
            content_id = tab.get("content_id"),
            media_type = MediaType(tab.get("media_type")),
            active = tab.get("active", True)
        )
