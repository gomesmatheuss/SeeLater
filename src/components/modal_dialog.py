import flet as ft
from datetime import datetime
from models.tab import Tab
from models.enums.priority import Priority
from services.process_json import extract_from_json
from services.db_service import save_tabs, save_tab

class CustomText(ft.Text):
    def __init__(self, text, color=None, size=16, text_align=ft.TextAlign.LEFT, tooltip=None, selectable=None):
        super().__init__()
        self.value = text
        self.expand = 1
        self.no_wrap = True
        self.overflow = ft.TextOverflow.ELLIPSIS
        self.size = size
        self.text_align = text_align
        self.tooltip = ft.Tooltip(text, wait_duration=ft.Duration(milliseconds=300)) if tooltip else None
        self.selectable = selectable
        if color:
            self.color = color


class TwoLineText(ft.Column):
    def __init__(self, label, text):
        super().__init__()
        self.spacing = 0
        self.expand = 1
        self.controls = [
            ft.Row(
                height = 13,
                expand = 1,
                controls = [
                    ft.Container(
                        padding = ft.padding.only(top=-6),
                        expand = 1,
                        content = ft.Text(
                            value = label,
                            color = ft.Colors.WHITE60,
                            max_lines = 1,
                            overflow = ft.TextOverflow.ELLIPSIS,
                            no_wrap = True,
                            size = 12
                        )
                    )
                ]
            ),
            ft.Row(
                height = 15,
                expand = 1,
                controls = [
                    ft.Container(
                        padding = ft.padding.only(top=-6),
                        expand = 1,
                        content = ft.Text(
                            value = text,
                            max_lines = 1,
                            overflow = ft.TextOverflow.ELLIPSIS,
                            no_wrap = True,
                            size = 16
                        )
                    )
                ]
            )
        ]


class ItemsExpansion(ft.ExpansionTile):
    def __init__(self, tab: Tab, refs: list):
        super().__init__("")
        tab.tags = ["Brave", "Musicas"]
        chk_ref = ft.Ref[ft.Checkbox]()
        refs.append(chk_ref)
        
        self.initially_expanded = False
        self.collapsed_text_color = ft.Colors.WHITE
        self.text_color = ft.Colors.PRIMARY
        self.bgcolor = ft.Colors.PRIMARY_CONTAINER
        self.min_tile_height = 1
        self.show_trailing_icon = False
        self.title = ft.Row(
            controls = [
                ft.Checkbox(value=True, ref=chk_ref),
                CustomText(tab.title, tooltip=True),
                CustomText(tab.url, tooltip=True)
            ]
        )
        self.controls = [
            ft.ListTile(
                min_vertical_padding = 5,
                min_height = 1,
                dense = True,
                bgcolor = ft.Colors.PRIMARY_CONTAINER,
                title = ft.Row(
                    controls = [
                        CustomText(tab.url, size=14, selectable=True)
                    ]
                )
            ),
            ft.ListTile(
                min_vertical_padding = 5,
                min_height = 1,
                dense = True,
                bgcolor = ft.Colors.PRIMARY_CONTAINER,
                title = ft.Row(
                    controls = [
                        TwoLineText("Index", tab.index),
                        TwoLineText("Prioridade", tab.priority),
                        TwoLineText("Tipo", tab.media_type)
                    ],
                    alignment = ft.MainAxisAlignment.START
                )
            ),
            ft.ListTile(
                min_vertical_padding = 5,
                min_height = 1,
                dense = True,
                bgcolor = ft.Colors.PRIMARY_CONTAINER,
                title = ft.Row(
                    wrap = True,
                    controls = [
                        ft.Container(
                            content = ft.Text(tag, color=ft.Colors.BLACK),
                            bgcolor = ft.Colors.YELLOW_200,
                            padding = 5,
                            border_radius = 3
                        )
                        for tag in tab.tags
                    ]
                )
            )
        ]
    

class DialogJson(ft.AlertDialog):
    def __init__(self, tabs, itens_count, tabs_count):
        super().__init__()
        self.tabs = tabs
        self.REFS_SELECTION = []

        self.modal = True
        self.title = ft.Text("Adicionar novo vídeo")
        self.content = ft.Column(
            expand=True,
            controls = [
                ft.Row(
                    controls=[
                        ft.Checkbox(),
                        ft.Text(f"0 / {tabs_count}")
                    ]
                ),
                ft.Divider(height=5),
                ft.ListView(
                    expand = 1,
                    width = 800,
                    controls = [
                        ItemsExpansion(tab, self.REFS_SELECTION)
                        for tab in self.tabs
                    ]
                )
            ]
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close),
            ft.TextButton("Salvar", on_click=self.save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def save(self, e):
        selected_tabs = [tab.to_dict() for tab, sel in zip(self.tabs, self.REFS_SELECTION) if sel.current.value]
        save_tabs(selected_tabs)
        self.close(e)

    def close(self, e):
        self.open = False
        self.page.update()


class Dialog(ft.AlertDialog):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

        self.url_field = ft.TextField(label="URL do vídeo", autofocus=True)
        self.priority_field = ft.Dropdown(
            label = "Prioridade",
            width = 300,
            options=[
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Baixa"),
            ],
            value = "Baixa"
        )
        self.tags_field = ft.TextField(label="Tags (separadas por vírgula)")
        self.upload_button = ft.OutlinedButton(
            text = "Selecione um arquivo", 
            height = 30,
            icon = ft.Icons.UPLOAD_FILE,
            on_click = self.pick_files
        )
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_files = ft.Text(size=10, color=ft.Colors.GREEN)

        self.modal = True
        self.title = ft.Text("Adicionar novo vídeo")
        self.content = ft.Column(
            controls = [
                self.url_field,
                self.priority_field,
                self.tags_field,
                ft.Divider(height=35),
                ft.Row(
                    [
                        ft.Text("ou com .json"),
                        self.upload_button
                    ]
                ),
                self.selected_files
            ],
            tight = True,
            height = 250,
            width = 400
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close),
            ft.TextButton("Salvar", on_click=self.save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def close(self, e):
        self.open = False
        self.page.update()

    def save(self, e):
        new_tab = Tab(
            url = self.url_field.value,
            title = self.url_field.value,
            index = 0,
            priority = Priority.MEDIUM if self.priority_field.value == "Média" else Priority.HIGH if self.priority_field.value == "Alta" else Priority.LOW,
            create_at = datetime.now(),
            last_update = datetime.now(),
            tags = [tag.strip() for tag in self.tags_field.value.split(",")] if self.tags_field.value else [],
            active = True
        )
        save_tab(new_tab)
        self.close(e)

    def pick_files(self, e):
        self.pick_files_dialog.pick_files(allowed_extensions=["json", "txt"], allow_multiple=False)

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        def on_close(e):
            dlg.open = False
            self.page.update()
            self.callback(True)

        self.selected_files.value = (
            json_path := f"{e.files[0].path}" if e.files else ""
        )
        self.selected_files.update()

        if json_path:
            tabs, json_count, tabs_count = extract_from_json(json_path)
            self.close(e)

            dlg = DialogJson(tabs, json_count, tabs_count)
            dlg.on_dismiss = on_close
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def did_mount(self):
        self.page.overlay.append(self.pick_files_dialog)
        self.page.update()

    def will_unmount(self):
        self.page.overlay.remove(self.pick_files_dialog)
        self.page.update()
