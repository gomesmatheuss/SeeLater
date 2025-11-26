import flet as ft
from models.video import Video

class EditVideo(ft.AlertDialog):
    def __init__(self, video: Video):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Editar Video")
        self.content = ft.Column(
            expand=True,
            controls = [
                ft.Row([
                    ft.Container(
                        expand=1,
                        content = ft.Image(
                            src=video.thumbnail_path,
                            # width=1280,
                            height=480,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(8),
                            aspect_ratio=1280/720,
                            expand=True
                        ),
                        # on_click=self.open_edit_video_dialog
                        # on_click = lambda x: x(page)
                    )                
                ]),
                ft.Row([
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=ft.Colors.GREY_700,
                        border_radius=20,
                        margin=ft.margin.only(top=2)
                    ),
                    # CardTexts(video),
                    ft.Column(
                        spacing=0,
                        controls = [
                            ft.PopupMenuButton(
                                padding=1,
                                menu_padding=1,
                                width=25,
                                items=[
                                    ft.PopupMenuItem(text="Item 1"),
                                    ft.PopupMenuItem(),
                                    ft.PopupMenuItem(
                                        text="Checked item",
                                        checked=False
                                    )
                                ]
                            ),
                            ft.Icon(ft.Icons.REFRESH)
                        ]
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.START)
            ]
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close),
            ft.TextButton("Salvar", on_click=self.save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def save(self, e):
        pass
    #     selected_tabs = [tab.to_dict() for tab, sel in zip(self.tabs, self.REFS_SELECTION) if sel.current.value]
    #     save_tabs(selected_tabs)
    #     self.close(e)

    def close(self, e):
        self.open = False
        self.page.update()