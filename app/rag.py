from pathlib import Path
from typing import Dict

#функция ниже загружает все .txt файлы из указанной папки(data).
#Возвращает словарь: {"имя_файла.txt": "содержимое"}
def load_docs(data_folder: str = "data") -> Dict[str, str]:
    documents = {}

    # определяем путь к папке data
    # если запускаем из корня проекта
    data_path = Path.cwd() / data_folder

    # если папка не найдена, пробуем найти ее у родителей
    if not data_path.exists():
        data_path = Path(__file__).parent.parent / data_folder

    if not data_path.exists():
        print(f"ПАПКА НЕ НАЙДЕНА: {data_path}")
        return documents

    for file_path in data_path.glob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # сохраняем данные в виде словаря, название:контент
                content = f.read().strip()
                documents[file_path.name] = content
        except Exception as e:
            print(f"ошибка чтения: {e}")

    print(f"всего загружено: {len(documents)} файлов")
    return documents

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
        "жильё": "benefits.txt",
        "страховка": "benefits.txt",
        "проезд": "benefits.txt",
        "сертификат": "benefits.txt",
        "тест": "general.txt",
        "собеседование": "general.txt",
        "анкета": "general.txt",
        "резюме": "general.txt",
        "студент": "general.txt",
        "стипендия": ["germany_rules.txt", "france_rules.txt"],
        "налог": ["germany_rules.txt", "france_rules.txt"],
        "виза": ["germany_rules.txt", "france_rules.txt"],
        "рабочий": ["germany_rules.txt", "france_rules.txt"],
        "евро": ["germany_rules.txt", "france_rules.txt"],
        "стажировка": "general.txt",
        "стажировки": "general.txt",
        "стажировке": "general.txt",
        "стажировку": "general.txt",
        "стажировкой": "general.txt",
    }

    country_specified = any(c in query_lower for c in ["германия", "франция", "берлин", "париж"])

    for keyword, target in keyword_to_file.items():
        if keyword in query_lower:

            # eсли target является списком файлов, как для стипендия, налог и тд.
            if isinstance(target, list):
                # если страна не указана то возвращаем оба файла объединёнными
                if not country_specified:
                    combined = ""
                    for fname in target:
                        if fname in documents:
                            combined += f"\n--- {fname} ---\n{documents[fname]}\n"
                    if combined:
                        return combined
                # если страна указана то пропускаем, ниже обработается отдельно
                else:
                    continue
            else:
                # target, это строка (имя одного файла)
                if target in documents:
                    return documents[target]

    # нам нужны все формы названий слов, потому что это критично влияет на нашу программу,
    # не верно указаня буква в названии страны и сразу же выводит ответ: Уточните страну?
    GERMANY_VARIANTS = [
        "германия", "германии", "германию", "германией", "германией",
        "берлин", "берлина", "берлину", "берлином", "берлине"
    ]

    FRANCE_VARIANTS = [
        "франция", "франции", "францию", "францией", "франциею",
        "париж", "парижа", "парижу", "парижем", "париже"
    ]

        # Отдельная проверка для случаев, когда пользователь написал только страну
    if any(variant in query_lower for variant in GERMANY_VARIANTS):
        if "germany_rules.txt" in documents:
            print(f"найдена страна: Германия")
            return documents["germany_rules.txt"]

    if any(variant in query for variant in FRANCE_VARIANTS):
        if "france_rules.txt" in documents:
            print(f"найдена страна: Франция")
            return documents["france_rules.txt"]

    if any(root in query_lower for root in ["стажировк", "анкет", "резюме", "собеседовани", "тестировани", "студент"]):
        return documents.get("general.txt", "")

    # елси не найдет совпадений, то выводит общую информацию
    return documents.get("general.txt", "Информация не найдена.")


if __name__ == '__main__':
    docs = load_docs()
    for name, content in docs.items():
        print(f'---{name}---')
        print(content[:100] + '...')