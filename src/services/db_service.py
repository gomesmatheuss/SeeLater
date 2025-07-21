from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["seelater"]
videos_collection = db["videos"]
tabs_collection = db["tabs"]

def save_video(video_dict):
    videos_collection.update_one(
        {"id": video_dict["id"]},
        {"$set": video_dict},
        upsert=True
    )

def save_tabs(tabs):
    tabs_collection.insert_many(tabs)

def get_all_videos():
    return list(videos_collection.find())

def get_tabs_list():
    return list(tabs_collection.find(limit=30))

def get_video_by_id(video_id):
    return videos_collection.find_one({"id": video_id})
