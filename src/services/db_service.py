import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["seelater"]
videos_collection = db["videos"]
tabs_collection = db["tabs"]
tags_collection = db["tags"]
groups_collection = db["groups"]

def save_video(video_dict):
    videos_collection.update_one(
        {"id": video_dict["id"]},
        {"$set": video_dict},
        upsert=True
    )

def save_tab(tab):
    tab.index = get_last_index() + 10 if tab.index == 0 else tab.index
    tabs_collection.update_one(
        {"url": tab.url},
        {"$set": tab.to_dict()},
        upsert=True
    )

def save_tabs(tabs):
    tabs_collection.insert_many(tabs)

def get_all_videos():
    return {video["id"]: video for video in videos_collection.find()}

def get_tabs_list():
    return list(tabs_collection.find({"active": True}).sort("index", -1))

def get_last_index():
    last_doc = list(tabs_collection.find({}, {"_id": 0, "index": 1}, limit=1).sort("index", -1))
    return last_doc[-1].get("index") if last_doc else -1

def get_video_by_id(video_id):
    return videos_collection.find_one({"id": video_id})

def set_watched(video_id):
    tabs_collection.update_one(
        {"url": f"https://www.youtube.com/watch?v={video_id}"},
        {"$set": {
            "active": False,
            "load_status": "watched",
            "last_update": datetime.now()
        }}
    )
    videos_collection.update_one(
        {"id": video_id},
        {"$set": {
            "active": False,
            "load_status": "watched",
            "last_update": datetime.now()
        }}
    )

# =========================
# TAGS
# =========================

def get_all_tags():
    """
    Retorna todas as tags cadastradas.
    """
    return list(
        tags_collection.find().sort("name", 1)
    )


def get_tag_by_id(tag_id):
    """
    Busca uma tag pelo seu ID.
    """
    from bson import ObjectId

    return tags_collection.find_one({
        "_id": ObjectId(tag_id)
    })


def save_tag(name, color="#2196F3", description=""):
    """
    Cria uma nova tag.
    """
    import re

    name = name.strip()
    description = description.strip()

    if not name:
        raise ValueError("O nome da tag não pode ficar vazio.")

    existing = tags_collection.find_one({
        "name": {
            "$regex": f"^{re.escape(name)}$",
            "$options": "i"
        }
    })

    if existing:
        raise ValueError("Já existe uma tag com esse nome.")

    result = tags_collection.insert_one({
        "name": name,
        "color": color,
        "description": description
    })

    return result.inserted_id


def update_tag(tag_id, name, color, description=""):
    """
    Atualiza o nome, a cor e a descrição de uma tag.
    """
    from bson import ObjectId
    import re

    name = name.strip()
    description = description.strip()

    if not name:
        raise ValueError("O nome da tag não pode ficar vazio.")

    existing = tags_collection.find_one({
        "name": {
            "$regex": f"^{re.escape(name)}$",
            "$options": "i"
        },
        "_id": {"$ne": ObjectId(tag_id)}
    })

    if existing:
        raise ValueError("Já existe outra tag com esse nome.")

    old_tag = get_tag_by_id(tag_id)

    if not old_tag:
        raise ValueError("Tag não encontrada.")

    old_name = old_tag["name"]

    tags_collection.update_one(
        {"_id": ObjectId(tag_id)},
        {
            "$set": {
                "name": name,
                "color": color,
                "description": description
            }
        }
    )

    if old_name != name:
        tabs_collection.update_many(
            {"tags": old_name},
            {"$set": {"tags.$[tag]": name}},
            array_filters=[{"tag": old_name}]
        )


def delete_tag(tag_id):
    """
    Exclui uma tag e remove suas referências dos vídeos.
    """
    from bson import ObjectId

    tag = get_tag_by_id(tag_id)

    if not tag:
        raise ValueError("Tag não encontrada.")

    tags_collection.delete_one({
        "_id": ObjectId(tag_id)
    })

    tabs_collection.update_many(
        {"tags": tag["name"]},
        {"$pull": {"tags": tag["name"]}}
    )



def get_all_tags_with_usage():
    """
    Retorna todas as tags com a quantidade de vídeos associados.
    """

    tags = get_all_tags()

    usage_results = tabs_collection.aggregate([
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "count": {"$sum": 1}
            }
        }
    ])

    usage = {
        item["_id"]: item["count"]
        for item in usage_results
    }

    for tag in tags:
        tag["usage_count"] = usage.get(tag["name"], 0)

    return tags



# =========================
# GROUPS
# =========================

def create_group(name, description=""):
    """
    Cria um novo agrupamento.
    """

    name = name.strip()
    description = description.strip()

    if not name:
        raise ValueError("O nome do agrupamento não pode ficar vazio.")

    existing = groups_collection.find_one({
        "name": {
            "$regex": f"^{name}$",
            "$options": "i"
        }
    })

    if existing:
        raise ValueError("Já existe um agrupamento com esse nome.")

    now = datetime.now()

    result = groups_collection.insert_one({
        "name": name,
        "description": description,
        "items": [],
        "created_at": now,
        "updated_at": now
    })

    return str(result.inserted_id)


def get_all_groups():
    """
    Retorna todos os agrupamentos.
    """

    return list(
        groups_collection.find().sort("created_at", -1)
    )


def get_group_by_id(group_id):
    """
    Busca um agrupamento pelo ID.
    """

    from bson import ObjectId

    return groups_collection.find_one({
        "_id": ObjectId(group_id)
    })


def update_group(group_id, name, description=""):
    """
    Atualiza as informações de um agrupamento.
    """

    from bson import ObjectId

    name = name.strip()
    description = description.strip()

    if not name:
        raise ValueError("O nome do agrupamento não pode ficar vazio.")

    existing = groups_collection.find_one({
        "name": {
            "$regex": f"^{name}$",
            "$options": "i"
        },
        "_id": {"$ne": ObjectId(group_id)}
    })

    if existing:
        raise ValueError("Já existe outro agrupamento com esse nome.")

    result = groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {
            "$set": {
                "name": name,
                "description": description,
                "updated_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError("Agrupamento não encontrado.")


def delete_group(group_id):
    """
    Exclui um agrupamento.
    Os vídeos originais não são afetados.
    """

    from bson import ObjectId

    result = groups_collection.delete_one({
        "_id": ObjectId(group_id)
    })

    if result.deleted_count == 0:
        raise ValueError("Agrupamento não encontrado.")


def add_item_to_group(group_id, media_type, media_id):
    """
    Adiciona um item ao agrupamento.

    O mesmo item pode pertencer a vários agrupamentos,
    mas não pode aparecer duplicado no mesmo agrupamento.
    """

    from bson import ObjectId

    item = {
        "media_type": media_type,
        "media_id": str(media_id)
    }

    result = groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {
            "$addToSet": {
                "items": item
            },
            "$set": {
                "updated_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError("Agrupamento não encontrado.")


def remove_item_from_group(group_id, media_type, media_id):
    """
    Remove um item de um agrupamento.
    Não exclui o item original do banco.
    """

    from bson import ObjectId

    result = groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {
            "$pull": {
                "items": {
                    "media_type": media_type,
                    "media_id": str(media_id)
                }
            },
            "$set": {
                "updated_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError("Agrupamento não encontrado.")


def reorder_group_items(group_id, items):
    """
    Atualiza a ordem dos itens de um agrupamento.
    """

    from bson import ObjectId

    result = groups_collection.update_one(
        {"_id": ObjectId(group_id)},
        {
            "$set": {
                "items": items,
                "updated_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError("Agrupamento não encontrado.")


def get_tabs_by_urls(urls):
    """
    Busca Tabs pelas URLs, independentemente do status ativo.
    """

    if not urls:
        return []

    return list(
        tabs_collection.find({
            "url": {"$in": urls}
        })
    )
