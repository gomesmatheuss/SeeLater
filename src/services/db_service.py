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

def save_tab(tab):
    tab.index = get_last_index() + 10
    tabs_collection.insert_one(tab.to_dict())

def save_tabs(tabs):
    tabs_collection.insert_many(tabs)

def get_all_videos():
    return list(videos_collection.find())

def get_tabs_list():
    return list(tabs_collection.find({"active": True}).sort("index", 1))

def get_last_index():
    last_doc = list(tabs_collection.find({}, {"_id": 0, "index": 1}, limit=1).sort("index", -1))
    return last_doc[-1].get("index") if last_doc else -1

def get_video_by_id(video_id):
    return videos_collection.find_one({"id": video_id})
