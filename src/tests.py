
from services.db_service import (
    create_group,
    create_group_item,
    get_group_items,
)

def main():
    print("Criando agrupamento de teste...")

    group_id = create_group(
        name="Grupo de teste - Cards",
        description="Agrupamento criado para testar os novos cards."
    )

    test_items = [
        {
            "media_type": "youtube_video",
            "media_id": "test_video_001",
            "url": "https://www.youtube.com/watch?v=ScMzIvxBSi4",
            "title": "Vídeo de teste 1 - Python",
            "priority": "low",
            "tags": [],
            "load_status": "json_imported",
            "index": 0,
        },
        {
            "media_type": "youtube_video",
            "media_id": "test_video_002",
            "url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
            "title": "Vídeo de teste 2 - Música",
            "priority": "medium",
            "tags": [],
            "load_status": "json_imported",
            "index": 10,
        },
        {
            "media_type": "youtube_video",
            "media_id": "test_video_003",
            "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "title": "Vídeo de teste 3 - Outro conteúdo",
            "priority": "high",
            "tags": [],
            "load_status": "json_imported",
            "index": 20,
        },
    ]

    for item in test_items:
        item_id = create_group_item(group_id, item)
        print(f"Item criado: {item_id} - {item['title']}")

    items = get_group_items(group_id)

    print(f"\nAgrupamento criado: {group_id}")
    print(f"Total de itens: {len(items)}")
    print("\nTeste concluído!")

if __name__ == "__main__":
    main()
