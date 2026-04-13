# импортируем библиотеки для чтения файла .env
import os
import warnings
from dotenv import load_dotenv

# я использую python 3.14 и pydantic на это ругается, решил сделать самое прямолинейное решение)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core")

# ищем файл .env и строим dict в котором будут переменные .env и их значение в виде {ключ:значение}
# этот файл находится в gitingonre и локально на пк,
# чтобы не выводить репо api ключи в открытый доступ
load_dotenv()


class MockLLM:
    """
    заглушка, иммитация ответов без llm,
    будет работать если в .env мы укажем mock,
    если у нас нет доступа к ключа нейронок.
    """

    # создаем функцию invoke поскольку так должны называться все методы langchain
    def invoke(self, messages):
        # берем текущий вопрос пользователя и превращаем ее в строку для дальнейшей обработки
        last_message = messages[-1]

        # обрабатываем два типа возвращенных данных,
        # поскольку content может быть как атрибутом так и ключом словаря.
        if hasattr(last_message, 'content'):
            content = last_message.content
        elif hasattr(last_message, 'get'):
            content = last_message.get('content', '')
        else:
            content = str(last_message)

        content_lower = content.lower()

        # для наглдяности печатаем сообщение пользователя(первые сто символов)
        print(f'получен запрос: {content[:100]}...')

        # ЛОГИКА ОТВЕТОВ
        # создаем новый класс типа 'Response', для того чтобы совпадали с объектом ответа LLM,
        # и приложение было автоматизировано.
        if 'германии' in content_lower or 'германия' in content_lower:
            return type('Response', (), {'content':'Согласно  базе, для стажировки в Германии ставка стипендии составляет 1200 евро в месяц, налог 15%. Рабочий день с 9:00 до 18:00.'})()
        elif 'франции' in content_lower or 'франция' in content_lower:
            return type('Response', (), {'content':'Согласно базе , для стажировки во Франции ставка стипендии составляет 1300 евро в месяц, налог 20%. Рабочий день с 10:00 до 19:00.'})()
        elif 'дедлайн' in content_lower:
            return type('Response', (), {'content': 'Дедлайн подачи документов — 25 апреля. Результаты отбора публикуются 1 мая.'})()
        elif 'стипендия' in content_lower:
            return type('Response', (), {'content': 'Для точного ответа о стипендии, уточните страну стажировки: Германия или Франция?'})()
        elif "жилье" in content_lower or "страховка" in content_lower:
            return type('Response', (), {'content': 'Стажерам предоставляется жилье в кампусе, оплачивается проезд и выдается страховка.'})()
        else:
            return type('Response', (), {'content': 'Программа международной стажировки "CdekStart" открыта для студентов последних курсов. Для участия необходимо заполнить анкету на сайте и приложить резюме. Отбор проходит в два этапа: тестирование и собеседование.'})()

def get_llm():
    """
    возвращает любую подключенную и настроенную llm
    Первоочерендно проверим на работующие llm, в другом случае вернем mockllm
    """

    DEFAULT_PROVIDER = "local"  # local / openai / compatible
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_BASE_URL = "http://localhost:11434/v1"
    DEFAULT_API_KEY = ""  # для openai и compatible
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 1000

    # я проверял только на локальной llm ollama
    if DEFAULT_PROVIDER == "local":
        try:
            from langchain_openai import ChatOpenAI
            print(f"использую локальную модель: {DEFAULT_MODEL} на {DEFAULT_BASE_URL}")

            return ChatOpenAI(
                model=DEFAULT_MODEL,
                base_url=DEFAULT_BASE_URL,
                api_key="not-needed",
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS
            )
        # при ошибке подключения будет запускаться if/else коснтрукция
        except Exception as e:
            return MockLLM()

        # --- OPENAI ---
    elif DEFAULT_PROVIDER == "openai":
            try:
                from langchain_openai import ChatOpenAI
                print(f"[LLM] OpenAI: {DEFAULT_MODEL}")
                return ChatOpenAI(
                    model=DEFAULT_MODEL,
                    api_key=DEFAULT_API_KEY,
                    temperature=DEFAULT_TEMPERATURE,
                    max_tokens=DEFAULT_MAX_TOKENS
                )
            except Exception as e:
                print(f"[LLM] Ошибка подключения к OpenAI: {e}")
                return MockLLM()

        # --- OPENAI-СОВМЕСТИМЫЕ (DeepSeek, Groq, Together, и т.д.) ---
    elif DEFAULT_PROVIDER == "compatible":
        try:
            from langchain_openai import ChatOpenAI
            print(f"[LLM] Совместимое API: {DEFAULT_MODEL} на {DEFAULT_BASE_URL}")
            return ChatOpenAI(
                model=DEFAULT_MODEL,
                base_url=DEFAULT_BASE_URL,
                api_key=DEFAULT_API_KEY,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS
            )
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return MockLLM()

    else:
        print(f"Неизвестный провайдер '{DEFAULT_PROVIDER}', использую MockLLM")
        return MockLLM()

if __name__ == '__main__':
    print('test')
    llm = get_llm()
    from langchain_core.messages import SystemMessage, HumanMessage
    test_messages = [
        SystemMessage(content="Ты консультант программы стажировки CdekStart. Отвечай кратко."),
        HumanMessage(content="Какая стипендия в Германии?")
    ]
    print("\nотправлем запрос...")
    response = llm.invoke(test_messages)
    print(f"\nответ LLM: {response.content}")