from pathlib import Path

def load_docs(data_folder: str = 'data') -> dict:
    documents_rag = {}
    data_path = Path.cwd().parent / data_folder

    print(f'поиск файлов в: {data_path}')
    if not data_path.exists():
        print(f'папка {data_path} не найдена')
        return documents_rag

    for file_path in data_path.glob('*.txt'):
        print(f'найден: {file_path.name}')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            documents_rag[file_path.name] = content
    return documents_rag

def search(query: str, documents:dict) -> str:
    query_lower = query.lower()
    keyword_to_file = {
        "германия": "germany_rules.txt",
        "берлин": "germany_rules.txt",
        "франция": "france_rules.txt",
        "париж": "france_rules.txt",
        "дедлайн": "deadlines.txt",
        "срок": "deadlines.txt",
        "дата": "deadlines.txt",
        "жилье": "benefits.txt",
        "страховка": "benefits.txt",
        "проезд": "benefits.txt",
        "тест": "general_info.txt",
        "собеседование": "general_info.txt",
        "анкета": "general_info.txt",
    }
    for keyword, filename in keyword_to_file.items():
        if keyword in query_lower:
            if filename in documents:
                print(f'Найдено по ключевому слову: "{keyword}":"{filename}"')
                return filename
    return documents.get("general_info.txt", "Информация не найдена")

if __name__ == '__main__':
    docs = load_docs()
    for name, content in docs.items():
        print(f'---{name}---')
        print(content[:100] + '...')