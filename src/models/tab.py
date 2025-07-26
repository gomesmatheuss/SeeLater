from datetime import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class Tab:
    url: str
    title: str
    index: int
    priority: str
    create_at: datetime
    tags: List[str] = None
    load_status: str = None
    content_id: str = None
    media_type: str = None
    active: bool = True

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "index": self.index,
            "priority": self.priority,
            "create_at": self.create_at,
            "tags": self.tags,
            "load_status": self.load_status,
            "content_id": self.content_id,
            "media_type": self.media_type,
            "active": self.active
        }
