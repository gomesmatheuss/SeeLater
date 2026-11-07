
from concurrent.futures import ThreadPoolExecutor
from threading import RLock

from models.enums.load_status import LoadStatus
from services.utils import get_yt_url_code
from services.video_service import get_video_info
from services.db_service import (
    save_video,
    update_video_load_status
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

        # Atualiza o status no banco dentro do worker.
        update_video_load_status(
            video_id,
            LoadStatus.LOADING,
            item["url"]
        )

        return self.processor(item)

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

            # Se já existe uma tarefa para esse vídeo,
            # apenas adiciona o novo callback.
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
                "callbacks": [],
                "url": url
            }

            if on_complete:
                self.tasks[video_id]["callbacks"].append(
                    on_complete
                )

            try:

                future = self.executor.submit(
                    self._run_processor,
                    video_id,
                    task_data
                )

                self.tasks[video_id]["future"] = future

                future.add_done_callback(
                    lambda result, vid=video_id:
                    self.on_task_complete(vid, result)
                )

            except Exception:

                self.tasks.pop(video_id, None)

                update_video_load_status(
                    video_id,
                    LoadStatus.LOAD_FAILED,
                    url
                )

                raise

        return True

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

        # Atualiza o status independentemente
        # do resultado do processamento.
        try:

            task_url = None

            with self.lock:
                task_url = self.tasks.get(
                    video_id, {}
                ).get("url")

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

        # Remove a tarefa e recupera os callbacks.
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

        # Executa os callbacks fora do lock.
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

    def get_status(self):

        with self.lock:

            running = sum(
                1
                for task in self.tasks.values()
                if task.get("future")
                and task["future"].running()
            )

            total = len(self.tasks)

            return {
                "total": total,
                "running": running,
                "waiting": total - running,
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
