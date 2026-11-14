
from concurrent.futures import TimeoutError
from threading import Event
from types import SimpleNamespace
import time

import services.video_queue_service as queue_module

from services.video_queue_service import VideoQueueService
from models.enums.load_status import LoadStatus


original_get_video_info = queue_module.get_video_info

events = {
    video_id: {
        "started": Event(),
        "release": Event(),
        "finished": Event()
    }
    for video_id in ("aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc")
}


def fake_get_video_info(item, force_refresh=False):

    video_id = item["url"].split("v=")[-1]
    event = events[video_id]

    event["started"].set()

    try:
        event["release"].wait(timeout=5)

        return SimpleNamespace(
            load_status=LoadStatus.LOAD_SUCCESS,
            url=item["url"],
            title=item["title"]
        )

    finally:
        event["finished"].set()


def wait_task_removed(queue, video_id, timeout=3):

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if not any(
            task["video_id"] == video_id
            for task in queue.get_tasks()
        ):
            return True

        time.sleep(0.02)

    return False


queue_module.get_video_info = fake_get_video_info


try:

    # ==========================================
    # TESTE 1: REMOVER TAREFA AGUARDANDO
    # ==========================================

    first_callback = Event()
    second_callback = Event()

    queue = VideoQueueService(max_workers=1)

    queue.enqueue_priority(
        {
            "url": "https://youtube.com/watch?v=aaaaaaaaaaa",
            "title": "Primeiro"
        },
        on_complete=lambda *args: first_callback.set()
    )

    assert events["aaaaaaaaaaa"]["started"].wait(timeout=2)

    callback_b = lambda *args: second_callback.set()

    queue.enqueue_priority(
        {
            "url": "https://youtube.com/watch?v=bbbbbbbbbbb",
            "title": "Segundo"
        },
        on_complete=callback_b
    )

    assert queue.remove_priority_callback(
        "bbbbbbbbbbb",
        callback_b
    )

    assert not any(
        task["video_id"] == "bbbbbbbbbbb"
        for task in queue.get_tasks()
    )

    events["aaaaaaaaaaa"]["release"].set()

    assert first_callback.wait(timeout=2)
    assert not events["bbbbbbbbbbb"]["started"].is_set()
    assert not second_callback.is_set()

    queue.shutdown(wait=True)

    print("OK: tarefa aguardando removida da fila.")

    # ==========================================
    # TESTE 2: PRESERVAR CALLBACK COMPARTILHADO
    # ==========================================

    first_callback = Event()
    shared_callback = Event()

    queue = VideoQueueService(max_workers=1)

    queue.enqueue_priority(
        {
            "url": "https://youtube.com/watch?v=ccccccccccc",
            "title": "Compartilhado"
        },
        on_complete=lambda *args: first_callback.set()
    )

    assert events["ccccccccccc"]["started"].wait(timeout=2)

    callback_shared = lambda *args: shared_callback.set()

    result = queue.enqueue_priority(
        {
            "url": "https://youtube.com/watch?v=ccccccccccc",
            "title": "Compartilhado"
        },
        on_complete=callback_shared
    )

    assert result is False

    assert queue.remove_priority_callback(
        "ccccccccccc",
        next(
            callback
            for callback in queue.tasks[
                ("priority", "ccccccccccc")
            ]["callbacks"]
            if callback is not callback_shared
        )
    )

    events["ccccccccccc"]["release"].set()

    assert shared_callback.wait(timeout=2)
    assert not first_callback.is_set()

    queue.shutdown(wait=True)

    print("OK: callback compartilhado preservado.")

    # ==========================================
    # TESTE 3: REMOVER CALLBACK EM EXECUÇÃO
    # ==========================================

    callback_called = Event()
    callback_running = lambda *args: callback_called.set()

    queue = VideoQueueService(max_workers=1)

    queue.enqueue_priority(
        {
            "url": "https://youtube.com/watch?v=bbbbbbbbbbb",
            "title": "Em execução"
        },
        on_complete=callback_running
    )

    assert events["bbbbbbbbbbb"]["started"].wait(timeout=2)

    assert queue.remove_priority_callback(
        "bbbbbbbbbbb",
        callback_running
    )

    # A tarefa continua executando mesmo sem o callback.
    assert any(
        task["video_id"] == "bbbbbbbbbbb"
        and task["status"] == "running"
        for task in queue.get_tasks()
    )

    events["bbbbbbbbbbb"]["release"].set()

    assert wait_task_removed(queue, "bbbbbbbbbbb")
    assert not callback_called.is_set()

    queue.shutdown(wait=True)

    print("OK: callback removido durante execução.")
    print("\nTodos os testes passaram!")


finally:

    for event in events.values():
        event["release"].set()

    queue_module.get_video_info = original_get_video_info
