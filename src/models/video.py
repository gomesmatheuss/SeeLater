class Video:
    def __init__(self, id, title, uploader, view_count, 
                 thumbnail_path, upload_date, duration, channel_id):
        self.id = id
        self.title = title
        self.uploader = uploader
        self.view_count = view_count
        self.thumbnail_path = thumbnail_path
        self.upload_date = upload_date 
        self.duration = duration
        self.channel_id = channel_id

    @staticmethod
    def from_dict(data):
        return Video(
            id=data["id"],
            title=data["title"],
            uploader=data["uploader"],
            view_count=data["view_count"],
            thumbnail_path=data["thumbnail_path"],
            upload_date=data["upload_date"],
            duration=data["duration"],
            channel_id=data["channel_id"]
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "uploader": self.uploader,
            "view_count": self.view_count,
            "thumbnail_path": self.thumbnail_path,
            "upload_date": self.upload_date,
            "duration": self.duration,
            "channel_id": self.channel_id,
        }
