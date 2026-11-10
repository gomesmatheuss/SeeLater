
import flet as ft

from services.video_queue_service import get_video_queue
from services.db_service import (
    get_queue_history,
    clear_queue_history
)


class DownloadsPage(ft.Column):

    def __init__(self, page):

        super().__init__()

        self.app_page = page
        self.queue = get_video_queue()

        self.mounted = False

        self.expand = True
        self.spacing = 15
        self.scroll = ft.ScrollMode.AUTO

        self.padding = ft.padding.only(
            left=20,
            right=20,
            top=15,
            bottom=15
        )

        # ==================================
        # CABEÇALHO
        # ==================================

        self.status_text = ft.Text(
            "Carregando...",
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.pause_button = ft.ElevatedButton(
            text="Pausar fila",
            icon=ft.Icons.PAUSE,
            on_click=self.toggle_queue
        )

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "Fila de carregamento",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
                self.pause_button
            ]
        )

        # ==================================
        # CONTADORES
        # ==================================

        self.running_count = ft.Text(
            "0",
            size=24,
            weight=ft.FontWeight.BOLD
        )

        self.waiting_count = ft.Text(
            "0",
            size=24,
            weight=ft.FontWeight.BOLD
        )

        counters = ft.Row(
            spacing=15,
            controls=[
                self.create_counter(
                    "Em processamento",
                    self.running_count
                ),
                self.create_counter(
                    "Aguardando",
                    self.waiting_count
                )
            ]
        )

        # ==================================
        # LISTAS DA FILA
        # ==================================

        self.running_list = ft.Column(
            spacing=8
        )

        self.waiting_list = ft.Column(
            spacing=8
        )

        # ==================================
        # HISTÓRICO DE CONCLUÍDOS
        # ==================================

        self.completed_count = ft.Text(
            "0",
            color=ft.Colors.ON_SURFACE_VARIANT
        )

        self.completed_list = ft.Column(
            spacing=8
        )

        self.clear_completed_button = ft.TextButton(
            text="Limpar concluídos",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=lambda e: self.confirm_clear_history(True)
        )

        completed_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Concluídos",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.completed_count
                    ]
                ),
                self.clear_completed_button
            ]
        )

        # ==================================
        # HISTÓRICO DE FALHAS
        # ==================================

        self.failed_count = ft.Text(
            "0",
            color=ft.Colors.ON_SURFACE_VARIANT
        )

        self.failed_list = ft.Column(
            spacing=8
        )

        self.clear_failed_button = ft.TextButton(
            text="Limpar falhas",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=lambda e: self.confirm_clear_history(False)
        )

        failed_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Falhas",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        self.failed_count
                    ]
                ),
                self.clear_failed_button
            ]
        )

        # ==================================
        # CONTEÚDO DA PÁGINA
        # ==================================

        self.controls = [

            header,
            self.status_text,
            counters,

            ft.Divider(),

            ft.Text(
                "Em processamento",
                size=18,
                weight=ft.FontWeight.BOLD
            ),
            self.running_list,

            ft.Divider(),

            ft.Text(
                "Aguardando",
                size=18,
                weight=ft.FontWeight.BOLD
            ),
            self.waiting_list,

            ft.Divider(),

            completed_header,
            self.completed_list,

            ft.Divider(),

            failed_header,
            self.failed_list
        ]

        self.refresh_interface()

    # ==================================
    # COMPONENTES
    # ==================================

    def create_counter(self, title, value):

        return ft.Container(
            expand=True,
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(
                        title,
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    value
                ]
            )
        )

    def create_task_tile(self, task):

        return ft.Container(
            padding=12,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        task["title"],
                        weight=ft.FontWeight.BOLD,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        task["url"],
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ]
            )
        )

    def create_history_tile(self, item, success):

        completed_at = item.get("completed_at")

        if completed_at:
            try:
                completed_at = completed_at.strftime(
                    "%d/%m/%Y às %H:%M"
                )
            except AttributeError:
                completed_at = str(completed_at)
        else:
            completed_at = "Data não disponível"

        icon = (
            ft.Icons.CHECK_CIRCLE
            if success
            else ft.Icons.ERROR
        )

        color = (
            ft.Colors.GREEN_400
            if success
            else ft.Colors.RED_400
        )

        controls = [

            ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(
                        icon,
                        color=color,
                        size=20
                    ),
                    ft.Text(
                        item.get("title") or "Título não disponível",
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    )
                ]
            ),

            ft.Text(
                item.get("url") or "",
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS
            ),

            ft.Text(
                completed_at,
                size=11,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ]

        # Exibe a mensagem de erro somente nas falhas.
        if not success and item.get("error"):

            controls.append(
                ft.Text(
                    f"Erro: {item['error']}",
                    size=12,
                    color=ft.Colors.RED_300,
                    max_lines=3,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            )

        return ft.Container(
            padding=12,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Column(
                spacing=5,
                controls=controls
            )
        )

    # ==================================
    # ATUALIZAÇÃO DA INTERFACE
    # ==================================

    def refresh_interface(self):

        status = self.queue.get_status()
        tasks = self.queue.get_tasks()

        self.status_text.value = (
            "Fila pausada"
            if status["paused"]
            else "Fila em execução"
        )

        self.status_text.color = (
            ft.Colors.ORANGE_400
            if status["paused"]
            else ft.Colors.GREEN_400
        )

        self.pause_button.text = (
            "Retomar fila"
            if status["paused"]
            else "Pausar fila"
        )

        self.pause_button.icon = (
            ft.Icons.PLAY_ARROW
            if status["paused"]
            else ft.Icons.PAUSE
        )

        self.running_count.value = str(status["running"])
        self.waiting_count.value = str(status["waiting"])

        running_tasks = [
            task for task in tasks
            if task["status"] == "running"
        ]

        waiting_tasks = [
            task for task in tasks
            if task["status"] == "waiting"
        ]

        self.running_list.controls = (
            [
                self.create_task_tile(task)
                for task in running_tasks
            ]
            if running_tasks
            else [
                ft.Text(
                    "Nenhum item em processamento.",
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ]
        )

        self.waiting_list.controls = (
            [
                self.create_task_tile(task)
                for task in waiting_tasks
            ]
            if waiting_tasks
            else [
                ft.Text(
                    "Nenhum item aguardando.",
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ]
        )

        # ==================================
        # ATUALIZA HISTÓRICO
        # ==================================

        completed = get_queue_history(success=True)
        failed = get_queue_history(success=False)

        self.completed_count.value = str(len(completed))
        self.failed_count.value = str(len(failed))

        self.clear_completed_button.disabled = not completed
        self.clear_failed_button.disabled = not failed

        self.completed_list.controls = (
            [
                self.create_history_tile(item, True)
                for item in completed
            ]
            if completed
            else [
                ft.Text(
                    "Nenhum item concluído.",
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ]
        )

        self.failed_list.controls = (
            [
                self.create_history_tile(item, False)
                for item in failed
            ]
            if failed
            else [
                ft.Text(
                    "Nenhuma falha registrada.",
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ]
        )

    # ==================================
    # LIMPEZA DO HISTÓRICO
    # ==================================

    def confirm_clear_history(self, success):

        category = (
            "concluídos"
            if success
            else "falhas"
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar limpeza"),
            content=ft.Text(
                f"Deseja realmente apagar todos os registros de {category}?"
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.app_page.close(dialog)
                ),
                ft.TextButton(
                    "Limpar",
                    on_click=lambda e: self.clear_history(
                        success,
                        dialog
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.app_page.open(dialog)

    def clear_history(self, success, dialog):

        self.app_page.close(dialog)

        try:

            removed = clear_queue_history(success)

            print(
                f"Histórico limpo: {removed} registros removidos."
            )

            self.refresh_interface()
            self.update()

        except Exception as e:

            print(
                "Erro ao limpar histórico:",
                e
            )

    # ==================================
    # CONTROLE DA FILA
    # ==================================

    def toggle_queue(self, e):

        if self.queue.is_paused():
            self.queue.resume()
        else:
            self.queue.pause()

        self.refresh_interface()
        self.update()

    # ==================================
    # ATUALIZAÇÃO AUTOMÁTICA
    # ==================================

    def did_mount(self):

        self.mounted = True

        self.app_page.run_task(
            self.refresh_loop
        )

    def will_unmount(self):

        self.mounted = False

    async def refresh_loop(self):

        import asyncio

        while self.mounted:

            await asyncio.sleep(5)

            if not self.mounted:
                break

            self.refresh_interface()
            self.update()
