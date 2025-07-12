import hashlib

def hash_video_url(url):
    return hashlib.md5(url.encode()).hexdigest()
