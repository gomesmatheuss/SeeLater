import flet as ft


class Pagination(ft.Row):

    def __init__(
        self,
        on_page_change,
        current_page=0,
        total_items=0,
        items_per_page=54
    ):
        super().__init__()

        self.on_page_change = on_page_change

        self.current_page = current_page
        self.total_items = total_items
        self.items_per_page = items_per_page

        self.alignment = ft.MainAxisAlignment.CENTER
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER

        self.update_controls()

    @property
    def total_pages(self):
        if self.total_items <= 0:
            return 1

        return (
            self.total_items + self.items_per_page - 1
        ) // self.items_per_page

    def set_data(
        self,
        current_page,
        total_items
    ):
        self.current_page = current_page
        self.total_items = total_items

        self.update_controls()

    def update_controls(self):

        total_pages = self.total_pages

        controls = []

        # Botão anterior
        controls.append(
            ft.TextButton(
                "Anterior",
                on_click=self.previous_page,
                disabled=self.current_page <= 0
            )
        )

        # Nenhuma página
        if total_pages <= 1:
            controls.append(
                self.create_page_button(0)
            )

        else:
            for page in self.get_page_numbers(total_pages):

                if page is None:
                    controls.append(
                        ft.Text("...")
                    )
                else:
                    controls.append(
                        self.create_page_button(page)
                    )

        # Botão próximo
        controls.append(
            ft.TextButton(
                "Próximo",
                on_click=self.next_page,
                disabled=self.current_page >= total_pages - 1
            )
        )

        self.controls = controls

    def create_page_button(self, page):

        return ft.TextButton(
            str(page + 1),
            on_click=lambda e, p=page: self.go_to_page(p),
            style=ft.ButtonStyle(
                bgcolor=(
                    ft.Colors.BLUE
                    if page == self.current_page
                    else None
                ),
                color=(
                    ft.Colors.WHITE
                    if page == self.current_page
                    else None
                )
            )
        )

    def get_page_numbers(self, total_pages):

        # Poucas páginas: mostra todas
        if total_pages <= 7:
            return list(range(total_pages))

        pages = []

        # Primeira página
        pages.append(0)

        # Região próxima da página atual
        start = max(
            1,
            self.current_page - 1
        )

        end = min(
            total_pages - 2,
            self.current_page + 1
        )

        # Reticências antes
        if start > 1:
            pages.append(None)

        # Páginas próximas
        for page in range(start, end + 1):
            pages.append(page)

        # Reticências depois
        if end < total_pages - 2:
            pages.append(None)

        # Última página
        pages.append(total_pages - 1)

        return pages

    def previous_page(self, e):

        if self.current_page <= 0:
            return

        self.go_to_page(
            self.current_page - 1
        )

    def next_page(self, e):

        if self.current_page >= self.total_pages - 1:
            return

        self.go_to_page(
            self.current_page + 1
        )

    def go_to_page(self, page):

        if page < 0 or page >= self.total_pages:
            return

        self.current_page = page

        self.update_controls()

        if self.on_page_change:
            self.on_page_change(page)
