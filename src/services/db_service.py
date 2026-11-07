import os
from pymongo import MongoClient
from datetime import datetime
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["seelater"]
videos_collection = db["videos"]
tabs_collection = db["tabs"]
tags_collection = db["tags"]
groups_collection = db["groups"]
group_items_collection = db["group_items"]
queue_history_collection = db["video_queue_history"]

group_items_collection.create_index(
    [("group_id", 1), ("url", 1)],
    unique=True,
    partialFilterExpression={"url": {"$type": "string"}},
    name="unique_url_per_group"
)

group_items_collection.create_index(
    [("group_id", 1), ("index", 1)],
    name="group_items_order"
)

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
        "created_at": now,
        "updated_at": now
    })

    return str(result.inserted_id)


def get_all_groups():
    return list(groups_collection.find().sort("created_at", -1))


def get_group_by_id(group_id):
    return groups_collection.find_one({
        "_id": ObjectId(group_id)
    })


def update_group(group_id, name, description=""):
    name = name.strip()
    description = description.strip()

    if not name:
        raise ValueError("O nome do agrupamento não pode ficar vazio.")

    group_object_id = ObjectId(group_id)

    existing = groups_collection.find_one({
        "name": {
            "$regex": f"^{name}$",
            "$options": "i"
        },
        "_id": {"$ne": group_object_id}
    })

    if existing:
        raise ValueError("Já existe outro agrupamento com esse nome.")

    result = groups_collection.update_one(
        {"_id": group_object_id},
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
    group_object_id = ObjectId(group_id)

    result = groups_collection.delete_one({
        "_id": group_object_id
    })

    if result.deleted_count == 0:
        raise ValueError("Agrupamento não encontrado.")

    # Exclui os itens pertencentes ao grupo.
    group_items_collection.delete_many({
        "group_id": group_object_id
    })


# --------------------------------------------------
# ITENS DOS GRUPOS
# --------------------------------------------------

def get_group_items(group_id):
    """
    Retorna todos os itens de um grupo, ordenados pelo índice.
    """

    return list(
        group_items_collection.find({
            "group_id": ObjectId(group_id)
        }).sort([
            ("index", 1),
            ("_id", 1)
        ])
    )


def get_group_item_by_id(group_id, item_id):
    """
    Busca um item específico dentro de um grupo.
    """

    return group_items_collection.find_one({
        "_id": ObjectId(item_id),
        "group_id": ObjectId(group_id)
    })


def get_group_item_by_url(group_id, url):
    """
    Verifica se uma URL já existe dentro do grupo.
    """

    return group_items_collection.find_one({
        "group_id": ObjectId(group_id),
        "url": url
    })


def get_next_group_item_index(group_id):
    """
    Retorna o próximo índice disponível no grupo.
    """

    last_item = group_items_collection.find_one(
        {"group_id": ObjectId(group_id)},
        sort=[("index", -1)]
    )

    return last_item.get("index", -10) + 10 if last_item else 0


def create_group_item(group_id, item_data):
    """
    Cria um novo item dentro de um grupo.

    Não consulta nem altera as coleções globais de vídeos e Tabs.
    """

    group_object_id = ObjectId(group_id)

    if not groups_collection.find_one({"_id": group_object_id}):
        raise ValueError("Agrupamento não encontrado.")

    item = dict(item_data)

    # Campos controlados pelo banco.
    item.pop("_id", None)
    item.pop("group_id", None)

    now = datetime.now()

    item["group_id"] = group_object_id
    item.setdefault("index", get_next_group_item_index(group_id))
    item.setdefault("created_at", now)
    item["updated_at"] = now

    try:
        result = group_items_collection.insert_one(item)
    except DuplicateKeyError:
        raise ValueError(
            "Este conteúdo já existe neste agrupamento."
        )

    groups_collection.update_one(
        {"_id": group_object_id},
        {"$set": {"updated_at": now}}
    )

    return str(result.inserted_id)


def update_group_item(group_id, item_id, updates):
    """
    Atualiza os dados de um item específico.
    """

    group_object_id = ObjectId(group_id)
    item_object_id = ObjectId(item_id)

    if not isinstance(updates, dict) or not updates:
        return

    updates = dict(updates)

    # Não permite alterar os identificadores e datas de criação.
    for field in ("_id", "group_id", "created_at"):
        updates.pop(field, None)

    updates["updated_at"] = datetime.now()

    try:
        result = group_items_collection.update_one(
            {
                "_id": item_object_id,
                "group_id": group_object_id
            },
            {"$set": updates}
        )
    except DuplicateKeyError:
        raise ValueError(
            "Este conteúdo já existe neste agrupamento."
        )

    if result.matched_count == 0:
        raise ValueError("Item não encontrado neste agrupamento.")

    groups_collection.update_one(
        {"_id": group_object_id},
        {"$set": {"updated_at": datetime.now()}}
    )


def remove_group_item(group_id, item_id):
    """
    Remove um item do grupo, sem afetar outros registros.
    """

    group_object_id = ObjectId(group_id)

    result = group_items_collection.delete_one({
        "_id": ObjectId(item_id),
        "group_id": group_object_id
    })

    if result.deleted_count == 0:
        raise ValueError("Item não encontrado neste agrupamento.")

    groups_collection.update_one(
        {"_id": group_object_id},
        {"$set": {"updated_at": datetime.now()}}
    )


def reorder_group_items(group_id, item_ids):
    """
    Atualiza a ordem dos itens de um grupo.

    Recebe uma lista de IDs na ordem desejada.
    """

    group_object_id = ObjectId(group_id)

    if not groups_collection.find_one({"_id": group_object_id}):
        raise ValueError("Agrupamento não encontrado.")

    object_ids = [ObjectId(item_id) for item_id in item_ids]

    existing_items = list(
        group_items_collection.find({
            "group_id": group_object_id,
            "_id": {"$in": object_ids}
        }, {"_id": 1})
    )

    if len(existing_items) != len(object_ids):
        raise ValueError(
            "A lista contém itens inexistentes ou de outro agrupamento."
        )

    for index, item_id in enumerate(object_ids):
        group_items_collection.update_one(
            {
                "_id": item_id,
                "group_id": group_object_id
            },
            {"$set": {"index": index * 10}}
        )

    groups_collection.update_one(
        {"_id": group_object_id},
        {"$set": {"updated_at": datetime.now()}}
    )

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

def update_video_load_status(video_id, status, url=None):
    """
    Atualiza o status de carregamento de um vídeo
    em todas as coleções relacionadas.

    Atualiza:
        - videos
        - tabs
        - group_items

    O ID do vídeo é utilizado como identificador principal.
    A URL serve como alternativa para registros antigos
    que ainda não possuem content_id ou media_id.
    """

    status = getattr(status, "value", status)
    now = datetime.now()

    # Atualiza ou cria o registro global do vídeo.
    videos_collection.update_one(
        {"id": video_id},
        {
            "$set": {
                "load_status": status,
                "last_update": now
            }
        },
        upsert=True
    )

    # Identifica as Tabs relacionadas.
    tab_conditions = [
        {"content_id": video_id}
    ]

    if url:
        tab_conditions.append({"url": url})

    tabs_collection.update_many(
        {"$or": tab_conditions},
        {
            "$set": {
                "load_status": status,
                "content_id": video_id,
                "last_update": now
            }
        }
    )

    # Identifica os itens dos grupos relacionados.
    group_item_conditions = [
        {"media_id": video_id}
    ]

    if url:
        group_item_conditions.append({"url": url})

    group_items_collection.update_many(
        {"$or": group_item_conditions},
        {
            "$set": {
                "load_status": status,
                "media_id": video_id,
                "updated_at": now
            }
        }
    )

# ==================================
# HISTÓRICO DA FILA DE CARREGAMENTO
# ==================================

def save_queue_history(video_id, title, url, success, error=None):
    """
    Registra o resultado de um carregamento na fila.
    """

    history_item = {
        "video_id": video_id,
        "title": title,
        "url": url,
        "success": success,
        "error": str(error) if error else None,
        "completed_at": datetime.now()
    }

    result = queue_history_collection.insert_one(
        history_item
    )

    return str(result.inserted_id)


def get_queue_history(success=None):
    """
    Retorna o histórico de carregamentos.

    success:
        True  = concluídos
        False = falhas
        None  = todos
    """

    query = {}

    if success is not None:
        query["success"] = success

    return list(
        queue_history_collection.find(query).sort(
            "completed_at", -1
        )
    )


def clear_queue_history(success):
    """
    Limpa o histórico de acordo com o resultado.

    True  = concluídos
    False = falhas
    """

    result = queue_history_collection.delete_many({
        "success": success
    })

    return result.deleted_count
