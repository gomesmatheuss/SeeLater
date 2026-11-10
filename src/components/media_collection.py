
import flet as ft

from components.pagination import Pagination


class MediaCollection(ft.Column):

    def __init__(
        self,
        on_page_change,
        card_builder,
        items_per_page=54,
        empty_message="Nenhum item encontrado."
    ):
        super().__init__()

        self.card_builder = card_builder
        self.empty_message = empty_message
        self.items_per_page = items_per_page

        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.HIDDEN

        self.cards_row = ft.Row(
            spacing=15,
            run_spacing=15,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.pagination = Pagination(
            on_page_change=on_page_change,
            current_page=0,
            total_items=0,
            items_per_page=self.items_per_page
        )

        self.controls = [
            self.cards_row,
            self.pagination
        ]

    def set_items(
        self,
        items,
        total_items,
        current_page
    ):

        self.cards_row.controls = [
            self.card_builder(item)
            for item in items
        ]

        if total_items == 0:
            self.cards_row.controls = [
                ft.Container(
                    padding=30,
                    content=ft.Text(
                        self.empty_message,
                        color=ft.Colors.GREY_400
                    )
                )
            ]

        self.pagination.set_data(
            current_page=current_page,
            total_items=total_items
        )
