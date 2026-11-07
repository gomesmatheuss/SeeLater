
from concurrent.futures import ThreadPoolExecutor
from threading import RLock

from models.enums.load_status import LoadStatus
from services.utils import get_yt_url_code
from services.video_service import get_video_info
from services.db_service import (
    save_video,
    update_video_load_status,
    save_queue_history
)


class VideoQueueService:

    def __init__(self, max_workers=2, processor=None):

        self.max_workers = max_workers

        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="VideoLoader"
        )

        self.processor = processor or self.process_video

        self.lock = RLock()

        self.tasks = {}

        self.paused = False

    # ==================================
    # PROCESSAMENTO
    # ==================================

    def process_video(self, item):

        video = get_video_info(item)

        if not video:
            raise RuntimeError(
                "Não foi possível obter as informações do vídeo."
            )

        if video.load_status != LoadStatus.LOAD_SUCCESS:
            raise RuntimeError(
                "O carregamento do vídeo não foi concluído."
            )

        save_video(video.to_dict())

        return video

    def _run_processor(self, video_id, item):

        update_video_load_status(
            video_id,
            LoadStatus.LOADING,
            item["url"]
        )

        return self.processor(item)

    # ==================================
    # CONTROLE INTERNO DA FILA
    # ==================================

    def _dispatch_pending_locked(self):

        started_tasks = []

        if self.paused:
            return started_tasks

        running = sum(
            1
            for task in self.tasks.values()
            if task.get("status") == "running"
        )

        for video_id, task in self.tasks.items():

            if running >= self.max_workers:
                break

            if task.get("status") != "waiting":
                continue

            future = self.executor.submit(
                self._run_processor,
                video_id,
                task["item"]
            )

            task["future"] = future
            task["status"] = "running"

            started_tasks.append(
                (video_id, future)
            )

            running += 1

        return started_tasks

    def _attach_callbacks(self, started_tasks):

        for video_id, future in started_tasks:

            future.add_done_callback(
                lambda result, vid=video_id:
                self.on_task_complete(vid, result)
            )

    # ==================================
    # ADICIONAR À FILA
    # ==================================

    def enqueue(self, item, on_complete=None):

        if not isinstance(item, dict):
            raise TypeError(
                "O item precisa ser um dicionário."
            )

        url = (item.get("url") or "").strip()

        if not url:
            raise ValueError(
                "O item não possui uma URL válida."
            )

        video_id = get_yt_url_code(url)

        if not video_id:
            raise ValueError(
                "Não foi possível identificar o ID do vídeo."
            )

        task_data = {
            "url": url,
            "title": item.get("title") or url
        }

        with self.lock:

            # Evita tarefas duplicadas.
            if video_id in self.tasks:

                if (
                    on_complete
                    and on_complete not in self.tasks[video_id]["callbacks"]
                ):
                    self.tasks[video_id]["callbacks"].append(
                        on_complete
                    )

                return False

            self.tasks[video_id] = {
                "item": task_data,
                "url": url,
                "status": "waiting",
                "future": None,
                "callbacks": (
                    [on_complete]
                    if on_complete
                    else []
                )
            }

            started_tasks = self._dispatch_pending_locked()

        self._attach_callbacks(started_tasks)

        return True

    # ==================================
    # PAUSAR E RETOMAR
    # ==================================

    def pause(self):

        with self.lock:
            self.paused = True

    def resume(self):

        with self.lock:

            self.paused = False

            started_tasks = self._dispatch_pending_locked()

        self._attach_callbacks(started_tasks)

    def is_paused(self):

        with self.lock:
            return self.paused

    # ==================================
    # FINALIZAÇÃO DA TAREFA
    # ==================================

    def on_task_complete(self, video_id, future):

        video = None
        error = None

        try:
            video = future.result()

        except Exception as e:

            error = e

            print(
                f"Erro ao carregar vídeo {video_id}:",
                e
            )

        # Recupera os dados da tarefa antes de removê-la.
        with self.lock:

            task = self.tasks.get(video_id)

            task_url = task["url"] if task else None

            task_title = (
                task["item"]["title"]
                if task
                else task_url
            )

        # Atualiza o status no banco.
        try:

            update_video_load_status(
                video_id,
                (
                    LoadStatus.LOAD_SUCCESS
                    if error is None
                    else LoadStatus.LOAD_FAILED
                ),
                video.url if video else task_url
            )

        except Exception as e:

            print(
                f"Erro ao atualizar status do vídeo {video_id}:",
                e
            )

            if error is None:
                error = e

        # Registra o resultado no histórico permanente.
        try:

            if task:

                save_queue_history(
                    video_id=video_id,
                    title=task_title,
                    url=task_url,
                    success=error is None,
                    error=error
                )

        except Exception as e:

            # Uma falha no histórico não deve interromper a fila.
            print(
                f"Erro ao salvar histórico do vídeo {video_id}:",
                e
            )

        # Remove a tarefa concluída e libera espaço na fila.
        with self.lock:

            task = self.tasks.pop(
                video_id,
                None
            )

            callbacks = (
                task["callbacks"]
                if task
                else []
            )

            # Inicia o próximo item somente se
            # a fila não estiver pausada.
            started_tasks = self._dispatch_pending_locked()

        self._attach_callbacks(started_tasks)

        # Executa os callbacks.
        for callback in callbacks:

            try:
                callback(
                    video_id,
                    video,
                    error
                )

            except Exception as e:

                print(
                    "Erro no callback da fila:",
                    e
                )

    # ==================================
    # INFORMAÇÕES DA FILA
    # ==================================

    def is_processing(self, video_id):

        with self.lock:
            return video_id in self.tasks

    def get_tasks(self):

        with self.lock:

            tasks = []

            for video_id, task in self.tasks.items():

                tasks.append({
                    "video_id": video_id,
                    "title": task["item"]["title"],
                    "url": task["url"],
                    "status": task["status"]
                })

            return tasks

    def get_status(self):

        with self.lock:

            running = sum(
                1
                for task in self.tasks.values()
                if task.get("status") == "running"
            )

            waiting = sum(
                1
                for task in self.tasks.values()
                if task.get("status") == "waiting"
            )

            return {
                "total": len(self.tasks),
                "running": running,
                "waiting": waiting,
                "paused": self.paused,
                "max_workers": self.max_workers
            }

    # ==================================
    # ENCERRAMENTO
    # ==================================

    def shutdown(self, wait=False):

        self.executor.shutdown(
            wait=wait,
            cancel_futures=False
        )


# ==================================
# INSTÂNCIA COMPARTILHADA
# ==================================

_video_queue = None
_video_queue_lock = RLock()


def get_video_queue():

    global _video_queue

    with _video_queue_lock:

        if _video_queue is None:
            _video_queue = VideoQueueService(max_workers=2)

        return _video_queue
