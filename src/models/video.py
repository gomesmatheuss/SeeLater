class Video:
    def __init__(self, id, title, uploader, view_count, thumbnail_path):
        self.id = id
        self.title = title
        self.uploader = uploader
        self.view_count = view_count
        self.thumbnail_path = thumbnail_path
        self.upload_date = None 
        self.duration = None

        self.channel_img_path = None
        self.channel_follower_count = None
        self.channel_is_verifield = None 
        self.channel_url = None 
        self.channel_id = None
        
