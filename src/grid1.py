import flet as ft

class Card(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 5
        self.content = ft.Column(
            alignment = ft.MainAxisAlignment.START,
            controls = [
                ft.Container(
                    content = ft.Image("./storage/temp/img_teste.jpg")
                ),
                ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.SUNNY, size=50),
                        ft.Column(
                            controls=[
                                ft.Text("Titulo"),
                                ft.Text("Canal"),
                                ft.Text("666 views"),
                                ft.Text("13 Visualizaçoes")
                            ]
                        )
                    ]
                )
            ]
        )

class Grid(ft.GridView):
    def __init__(self):
        super().__init__()
        self.runs_count = 5
        self.max_extent = 400
        self.child_aspect_ratio = 1.0
        self.spacing = 5
        self.run_spacing = 5
        self.controls = [
            Card(),
            Card(),
            Card(),
            ft.Placeholder(),
            ft.Placeholder(),
            ft.Placeholder(),
            ft.Placeholder(),
            ft.Placeholder(),
            ft.Placeholder(),
        ]
