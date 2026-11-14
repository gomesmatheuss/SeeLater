
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

        self.default_processor = processor is None
        self.processor = processor or self.process_video

        self.lock = RLock()
        self.tasks = {}
        self.paused = False

    # ==================================
    # PROCESSAMENTO
    # ==================================

    def process_video(self, item, force_refresh=False):

        video = get_video_info(
            item,
            force_refresh=force_refresh
        )

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

    def _run_processor(
        self,
        video_id,
        item,
        force_refresh=False,
        metadata_only=False
    ):

        # Solicitações exclusivas do importador.
        # Não alteram o status nem salvam o vídeo no banco.
        if metadata_only:

            video = get_video_info(
                item,
                force_refresh=True
            )

            if not video:
                raise RuntimeError(
                    "Não foi possível obter as informações do vídeo."
                )

            if video.load_status != LoadStatus.LOAD_SUCCESS:
                raise RuntimeError(
                    "O carregamento do vídeo não foi concluído."
                )

            return video

        update_video_load_status(
            video_id,
            LoadStatus.LOADING,
            item["url"]
        )

        if self.default_processor:
            return self.process_video(
                item,
                force_refresh=force_refresh
            )

        return self.processor(item)

    # ==================================
    # CONTROLE INTERNO DA FILA
    # ==================================

    def _dispatch_pending_locked(self):

        started_tasks = []

        running = sum(
            1
            for task in self.tasks.values()
            if task.get("status") == "running"
        )

        # Prioritárias primeiro.
        # A ordem original é preservada dentro de cada prioridade.
        ordered_tasks = sorted(
            self.tasks.items(),
            key=lambda entry: not entry[1].get("priority", False)
        )

        for task_key, task in ordered_tasks:

            if running >= self.max_workers:
                break

            if task.get("status") != "waiting":
                continue

            is_priority = task.get("priority", False)

            # Com a fila pausada, somente prioritárias iniciam.
            if self.paused and not is_priority:
                continue

            future = self.executor.submit(
                self._run_processor,
                task["video_id"],
                task["item"],
                task.get("force_refresh", False),
                task.get("metadata_only", False)
            )

            task["future"] = future
            task["status"] = "running"

            started_tasks.append(
                (task_key, future)
            )

            running += 1

        return started_tasks

    def _attach_callbacks(self, started_tasks):

        for task_key, future in started_tasks:

            future.add_done_callback(
                lambda result, key=task_key:
                self.on_task_complete(key, result)
            )

    # ==================================
    # ADICIONAR À FILA
    # ==================================

    def _enqueue(
        self,
        item,
        on_complete=None,
        priority=False,
        metadata_only=False
    ):

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

        # Cada modalidade possui sua própria identificação.
        task_key = (
            "priority" if priority else "normal",
            video_id
        )

        task_data = {
            "url": url,
            "title": item.get("title") or url
        }

        with self.lock:

            # Evita duplicidade dentro da mesma modalidade.
            if task_key in self.tasks:

                existing_task = self.tasks[task_key]

                if (
                    on_complete
                    and on_complete not in existing_task["callbacks"]
                ):
                    existing_task["callbacks"].append(
                        on_complete
                    )

                started_tasks = self._dispatch_pending_locked()
                result = False

            else:

                self.tasks[task_key] = {
                    "video_id": video_id,
                    "item": task_data,
                    "url": url,
                    "status": "waiting",
                    "future": None,
                    "callbacks": (
                        [on_complete]
                        if on_complete
                        else []
                    ),
                    "priority": priority,
                    "force_refresh": priority,
                    "metadata_only": metadata_only
                }

                started_tasks = self._dispatch_pending_locked()
                result = True

        self._attach_callbacks(started_tasks)

        return result

    def enqueue(self, item, on_complete=None):

        return self._enqueue(
            item,
            on_complete=on_complete
        )

    def enqueue_priority(self, item, on_complete=None):

        return self._enqueue(
            item,
            on_complete=on_complete,
            priority=True,
            metadata_only=True
        )

    def remove_priority_callback(self, video_id, callback):
        """
        Remove somente o callback de uma solicitação prioritária.

        Se a tarefa ainda estiver aguardando e não possuir
        outros callbacks, ela será removida da fila.

        Tarefas em execução não são interrompidas.
        """

        task_key = ("priority", video_id)

        with self.lock:

            task = self.tasks.get(task_key)

            if not task:
                return False

            callbacks = task["callbacks"]

            if callback not in callbacks:
                return False

            callbacks.remove(callback)

            started_tasks = []

            if task["status"] == "waiting" and not callbacks:

                self.tasks.pop(task_key, None)

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

    def on_task_complete(self, task_key, future):

        video = None
        error = None

        try:
            video = future.result()

        except Exception as e:

            error = e

            print(
                f"Erro ao carregar vídeo {task_key[1]}:",
                e
            )

        # Recupera os dados antes de remover a tarefa.
        with self.lock:

            task = self.tasks.get(task_key)

            video_id = task["video_id"] if task else task_key[1]
            task_url = task["url"] if task else None

            task_title = (
                task["item"]["title"]
                if task
                else task_url
            )

            metadata_only = (
                task.get("metadata_only", False)
                if task
                else False
            )

        # Solicitações exclusivas do importador não alteram
        # o status nem o histórico da fila normal.
        if not metadata_only:

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

                print(
                    f"Erro ao salvar histórico do vídeo {video_id}:",
                    e
                )

        # Remove a tarefa e libera espaço na fila.
        with self.lock:

            task = self.tasks.pop(
                task_key,
                None
            )

            callbacks = (
                task["callbacks"]
                if task
                else []
            )

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

            return (
                ("normal", video_id) in self.tasks
                or ("priority", video_id) in self.tasks
            )

    def get_tasks(self):

        with self.lock:

            tasks = []

            for task in self.tasks.values():

                tasks.append({
                    "video_id": task["video_id"],
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
