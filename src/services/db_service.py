from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["seelater"]
videos_collection = db["videos"]
list_collection = db["videos_list"]

def save_video(video_dict):
    videos_collection.update_one(
        {"id": video_dict["id"]},
        {"$set": video_dict},
        upsert=True
    )

def get_all_videos():
    return list(videos_collection.find())

def get_list_videos():
    return list(list_collection.find())

def get_video_by_id(video_id):
    return videos_collection.find_one({"id": video_id})
