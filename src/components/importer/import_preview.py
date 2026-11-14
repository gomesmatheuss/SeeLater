
import flet as ft

from components.importer.import_item_card import ImportItemCard


class ImportPreview(ft.ListView):
    """
    Componente responsável pela apresentação da lista
    de itens na pré-visualização do importador.
    """

    def __init__(
        self,
        available_tags,
        on_selection,
        on_media_type_change,
        on_remove,
        on_load_metadata=None
    ):
        self.available_tags = available_tags
        self.on_selection = on_selection
        self.on_media_type_change = on_media_type_change
        self.on_remove = on_remove
        self.on_load_metadata = on_load_metadata

        super().__init__(
            expand=True,
            spacing=5,
            controls=[]
        )

    def set_items(self, items):

        self.controls = [
            ImportItemCard(
                item=item,
                index=index,
                available_tags=self.available_tags,
                on_selection=self.on_selection,
                on_media_type_change=self.on_media_type_change,
                on_remove=self.on_remove,
                on_load_metadata=self.on_load_metadata
            )
            for index, item in enumerate(items)
        ]
