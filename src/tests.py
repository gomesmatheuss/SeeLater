
import time
from uuid import uuid4
from types import SimpleNamespace
from threading import Lock

from bson import ObjectId

from services.video_queue_service import VideoQueueService
from services.db_service import (
    videos_collection,
    tabs_collection,
    group_items_collection
)


completed = []
attempts = {}
counter_lock = Lock()


def fake_processor(item):
    url = item["url"]
    title = item["title"]

    with counter_lock:
        attempts[url] = attempts.get(url, 0) + 1
        attempt = attempts[url]

    print(f"Iniciando: {title} - tentativa {attempt}")

    time.sleep(1)

    if title == "Vídeo B" and attempt == 1:
        raise RuntimeError("Falha simulada.")

    print(f"Finalizado: {title}")

    return SimpleNamespace(
        url=url,
        title=title
    )


def on_complete(video_id, video, error):
    completed.append({
        "id": video_id,
        "error": error
    })

    print(
        f"Callback: {video_id} - "
        f"{'Erro' if error else 'Sucesso'}"
    )


def wait_queue(queue):
    while queue.get_status()["total"] > 0:
        time.sleep(0.1)


# IDs temporários válidos para o YouTube.
video_a_id = uuid4().hex[:11]
video_b_id = uuid4().hex[:11]

video_a_url = f"https://www.youtube.com/watch?v={video_a_id}"
video_b_url = f"https://www.youtube.com/watch?v={video_b_id}"

group_id_1 = ObjectId()
group_id_2 = ObjectId()

test_ids = [video_a_id, video_b_id]
test_urls = [video_a_url, video_b_url]
group_ids = [group_id_1, group_id_2]

queue = VideoQueueService(
    max_workers=2,
    processor=fake_processor
)

try:
    print("\nCriando registros temporários...\n")

    for video_id, url in zip(test_ids, test_urls):

        videos_collection.insert_one({
            "id": video_id,
            "load_status": "ready_for_load"
        })

        tabs_collection.insert_one({
            "url": url,
            "content_id": video_id,
            "load_status": "ready_for_load"
        })

    # Vídeo A aparece em dois grupos.
    group_items_collection.insert_many([
        {
            "group_id": group_id_1,
            "url": video_a_url,
            "media_id": video_a_id,
            "load_status": "ready_for_load"
        },
        {
            "group_id": group_id_2,
            "url": video_a_url,
            "media_id": video_a_id,
            "load_status": "ready_for_load"
        },
        {
            "group_id": group_id_1,
            "url": video_b_url,
            "media_id": video_b_id,
            "load_status": "ready_for_load"
        }
    ])

    print("Registros criados.")

    # ==================================
    # PRIMEIRA EXECUÇÃO
    # ==================================

    print("\nAdicionando vídeos à fila...\n")

    queue.enqueue(
        {"url": video_a_url, "title": "Vídeo A"},
        on_complete
    )

    queue.enqueue(
        {"url": video_b_url, "title": "Vídeo B"},
        on_complete
    )

    # Confere o status durante o processamento.
    video_a = videos_collection.find_one({"id": video_a_id})
    video_b = videos_collection.find_one({"id": video_b_id})

    assert video_a["load_status"] == "loading"
    assert video_b["load_status"] == "loading"

    print("Status LOADING confirmado.")

    wait_queue(queue)

    # Vídeo A deve ter sido concluído.
    video_a = videos_collection.find_one({"id": video_a_id})
    tab_a = tabs_collection.find_one({"url": video_a_url})

    group_a_items = list(
        group_items_collection.find({"media_id": video_a_id})
    )

    assert video_a["load_status"] == "load_success"
    assert tab_a["load_status"] == "load_success"
    assert len(group_a_items) == 2

    assert all(
        item["load_status"] == "load_success"
        for item in group_a_items
    )

    # Vídeo B deve ter falhado.
    video_b = videos_collection.find_one({"id": video_b_id})
    tab_b = tabs_collection.find_one({"url": video_b_url})

    group_b_item = group_items_collection.find_one({
        "media_id": video_b_id
    })

    assert video_b["load_status"] == "load_failed"
    assert tab_b["load_status"] == "load_failed"
    assert group_b_item["load_status"] == "load_failed"

    print("\nPrimeira execução validada!")

    # ==================================
    # NOVA TENTATIVA
    # ==================================

    print("\nReenfileirando Vídeo B...\n")

    queue.enqueue(
        {"url": video_b_url, "title": "Vídeo B"},
        on_complete
    )

    wait_queue(queue)

    video_b = videos_collection.find_one({"id": video_b_id})
    tab_b = tabs_collection.find_one({"url": video_b_url})

    group_b_item = group_items_collection.find_one({
        "media_id": video_b_id
    })

    assert video_b["load_status"] == "load_success"
    assert tab_b["load_status"] == "load_success"
    assert group_b_item["load_status"] == "load_success"

    assert attempts[video_b_url] == 2

    print("\n========== RESULTADO ==========")
    print("Callbacks executados:", len(completed))
    print("Tentativas do Vídeo B:", attempts[video_b_url])

    print("\nTodos os testes passaram!")

finally:
    queue.shutdown(wait=True)

    videos_collection.delete_many({
        "id": {"$in": test_ids}
    })

    tabs_collection.delete_many({
        "url": {"$in": test_urls}
    })

    group_items_collection.delete_many({
        "group_id": {"$in": group_ids}
    })

    print("\nRegistros temporários removidos.")
