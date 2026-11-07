from services.db_service import get_queue_history

history = get_queue_history()

print("\nHISTÓRICO DA FILA")
print(f"Total de registros: {len(history)}")

for item in history[:10]:

    status = "SUCESSO" if item["success"] else "FALHA"

    print("\n------------------------------")
    print("Status:", status)
    print("Título:", item["title"])
    print("ID:", item["video_id"])
    print("URL:", item["url"])
    print("Erro:", item.get("error"))
    print("Concluído em:", item["completed_at"])
