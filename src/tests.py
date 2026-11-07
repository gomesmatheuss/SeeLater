
import time
import threading

from types import SimpleNamespace

import services.video_queue_service as queue_module
from services.video_queue_service import VideoQueueService


# ==========================================
# CONFIGURAÇÃO DOS TESTES
# ==========================================

VIDEOS = {
    "Vídeo A": "https://www.youtube.com/watch?v=aaaaaa00001",
    "Vídeo B": "https://www.youtube.com/watch?v=aaaaaa00002",
    "Vídeo C": "https://www.youtube.com/watch?v=aaaaaa00003",
    "Vídeo D": "https://www.youtube.com/watch?v=aaaaaa00004",
    "Vídeo E": "https://www.youtube.com/watch?v=aaaaaa00005",
}

started_events = {
    name: threading.Event()
    for name in VIDEOS
}

release_events = {
    name: threading.Event()
    for name in VIDEOS
}

started_videos = []
completed_videos = []

active_workers = 0
max_active_workers = 0

test_lock = threading.RLock()


# ==========================================
# PROCESSADOR SIMULADO
# ==========================================

def fake_processor(item):

    global active_workers
    global max_active_workers

    title = item["title"]

    with test_lock:

        active_workers += 1

        max_active_workers = max(
            max_active_workers,
            active_workers
        )

        started_videos.append(title)

        print(f"Iniciando: {title}")

        started_events[title].set()

    # Simula um download em andamento.
    released = release_events[title].wait(timeout=15)

    with test_lock:
        active_workers -= 1

    if not released:
        raise TimeoutError(
            f"Timeout no processamento de {title}"
        )

    print(f"Finalizado: {title}")

    return SimpleNamespace(
        url=item["url"]
    )


# ==========================================
# CALLBACK
# ==========================================

def on_complete(video_id, video, error):

    title = video_id

    with test_lock:
        completed_videos.append(
            (video_id, error)
        )

    if error:
        print(f"Callback com erro: {title}")

    else:
        print(f"Callback concluído: {title}")


# ==========================================
# AUXILIARES
# ==========================================

def wait_for_event(event, description, timeout=5):

    if not event.wait(timeout):

        raise AssertionError(
            f"Tempo esgotado aguardando: {description}"
        )


def wait_for_condition(condition, description, timeout=5):

    start = time.monotonic()

    while time.monotonic() - start < timeout:

        if condition():
            return

        time.sleep(0.05)

    raise AssertionError(
        f"Tempo esgotado aguardando: {description}"
    )


def enqueue_video(queue, name):

    queue.enqueue(
        {
            "url": VIDEOS[name],
            "title": name
        },
        on_complete=on_complete
    )


# ==========================================
# TESTE PRINCIPAL
# ==========================================

def run_tests():

    global max_active_workers

    # Impede qualquer alteração no MongoDB.
    queue_module.update_video_load_status = (
        lambda *args, **kwargs: None
    )

    queue = VideoQueueService(
        max_workers=2,
        processor=fake_processor
    )

    try:

        # ----------------------------------
        # TESTE 1: FILA NORMAL
        # ----------------------------------

        print("\nTESTE 1: FILA NORMAL")

        for name in [
            "Vídeo A",
            "Vídeo B",
            "Vídeo C",
            "Vídeo D"
        ]:
            enqueue_video(queue, name)

        wait_for_event(
            started_events["Vídeo A"],
            "início do Vídeo A"
        )

        wait_for_event(
            started_events["Vídeo B"],
            "início do Vídeo B"
        )

        status = queue.get_status()

        assert status["running"] == 2
        assert status["waiting"] == 2

        print("Dois downloads iniciados.")
        print("Dois downloads aguardando.")

        # ----------------------------------
        # TESTE 2: PAUSAR A FILA
        # ----------------------------------

        print("\nTESTE 2: PAUSAR A FILA")

        queue.pause()

        assert queue.is_paused()

        print("Fila pausada.")

        # Finaliza somente o primeiro vídeo.
        release_events["Vídeo A"].set()

        wait_for_condition(
            lambda: any(
                error is None
                for _, error in completed_videos
            ),
            "finalização do Vídeo A"
        )

        time.sleep(0.2)

        assert "Vídeo C" not in started_videos
        assert "Vídeo D" not in started_videos

        status = queue.get_status()

        assert status["paused"] is True
        assert status["running"] == 1
        assert status["waiting"] == 2

        print("Fila permaneceu pausada.")
        print("Nenhum novo download foi iniciado.")

        # ----------------------------------
        # TESTE 3: NOVOS ITENS DURANTE PAUSA
        # ----------------------------------

        print("\nTESTE 3: NOVOS ITENS DURANTE PAUSA")

        enqueue_video(queue, "Vídeo E")

        time.sleep(0.2)

        assert "Vídeo E" not in started_videos

        status = queue.get_status()

        assert status["running"] == 1
        assert status["waiting"] == 3
        assert status["paused"] is True

        print("Vídeo E adicionado à fila.")
        print("Vídeo E permaneceu aguardando.")

        # ----------------------------------
        # TESTE 4: RETOMAR A FILA
        # ----------------------------------

        print("\nTESTE 4: RETOMAR A FILA")

        queue.resume()

        assert not queue.is_paused()

        wait_for_event(
            started_events["Vídeo C"],
            "início do Vídeo C"
        )

        status = queue.get_status()

        assert status["running"] == 2
        assert status["waiting"] == 2

        print("Fila retomada.")
        print("Vídeo C iniciado.")

        # Finaliza B: D deve iniciar.
        release_events["Vídeo B"].set()

        wait_for_event(
            started_events["Vídeo D"],
            "início do Vídeo D"
        )

        # Finaliza C: E deve iniciar.
        release_events["Vídeo C"].set()

        wait_for_event(
            started_events["Vídeo E"],
            "início do Vídeo E"
        )

        # Finaliza os últimos downloads.
        release_events["Vídeo D"].set()
        release_events["Vídeo E"].set()

        wait_for_condition(
            lambda: len(completed_videos) == 5,
            "finalização de todos os vídeos"
        )

        # ----------------------------------
        # VALIDAÇÕES FINAIS
        # ----------------------------------

        print("\nVALIDAÇÕES FINAIS")

        assert len(started_videos) == 5
        assert len(completed_videos) == 5

        assert max_active_workers == 2

        assert all(
            error is None
            for _, error in completed_videos
        )

        assert started_videos == [
            "Vídeo A",
            "Vídeo B",
            "Vídeo C",
            "Vídeo D",
            "Vídeo E"
        ]

        status = queue.get_status()

        assert status["total"] == 0
        assert status["running"] == 0
        assert status["waiting"] == 0

        print("Ordem dos downloads:", started_videos)
        print("Concorrência máxima:", max_active_workers)
        print("Todos os callbacks executados.")

        print("\nTODOS OS TESTES PASSARAM!")

    finally:

        # Libera qualquer worker que ainda esteja aguardando.
        for event in release_events.values():
            event.set()

        queue.shutdown(wait=True)


if __name__ == "__main__":
    run_tests()
