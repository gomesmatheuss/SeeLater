import hashlib
import re

def hash_video_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def get_yt_url_code(url):
    url_code = re.findall(r'\?v=(.*?)$', url)
    return url_code[0] if url_code else None
