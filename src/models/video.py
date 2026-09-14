from datetime import datetime
from dataclasses import dataclass
from models.enums.load_status import LoadStatus
from models.enums.media_type import MediaType


@dataclass
class Video:
    id: str
    url: str
    title: str
    uploader: str
    view_count: int
    thumbnail_path: str
    upload_date: datetime
    duration: str
    channel_id: str = None
    channel_thumbnail_path: str = None
    last_update: datetime = datetime.now()
    load_status: LoadStatus = LoadStatus.LOAD_FAILED
    media_type: MediaType = MediaType.OTHER_SITE
    active: bool = True

    @staticmethod
    def from_dict(data):
        return Video(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            uploader=data["uploader"],
            view_count=data["view_count"],
            thumbnail_path=data["thumbnail_path"],
            upload_date=data["upload_date"],
            duration=data["duration"],
            channel_id=data.get("channel_id"),
            channel_thumbnail_path=data.get("channel_thumbnail_path"),
            last_update=data["last_update"],
            load_status=LoadStatus(data["load_status"]),
            media_type=MediaType(data["media_type"]),
            active=data["active"]
        )

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "uploader": self.uploader,
            "view_count": self.view_count,
            "thumbnail_path": self.thumbnail_path,
            "upload_date": self.upload_date,
            "duration": self.duration,
            "channel_id": self.channel_id,
            "channel_thumbnail_path": self.channel_thumbnail_path,
            "last_update": self.last_update,
            "load_status": self.load_status.value,
            "media_type": self.media_type.value,
            "active": self.active
        }
