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
    в зависимости от содержания .env
    Первоочерендно проверим на работующие llm, в другом случае вернем mockllm
    """

    # если переменная LLM_PROVIDER не будет найдена в .env, будем использовать логику класса mock_llm
    provider = os.getenv('LLM_PROVIDER', "mock").lower()

    # в пример я взял deepseek, но если нужно что то другое,
    # мы просто добавим в .env новые переменные и перепишем логику ниже на другую llm
    if provider == 'deepseek':
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print('Ключ deepseek не найден, используем mockLLM')
            return MockLLM
        try:
            # импортируем внутри функции потому что, если отсутствует ключ, то библиотека будет занимать лишние ресурсы,
            # также для того чтобы обработать ошибки ImportError и Exception(проблемы с ключом)
            from langchain_openai import ChatOpenAI

            # берем характеристики из .env, и на всякий случай делаем дефолтные если переменная не найдется
            model = os.getenv("LLM_MODEL", "deepseek-chat")
            base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
            max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))

            print(f'используется deepseek: {model}')
            print(f'base url: {base_url}')

            return ChatOpenAI(
                model = model,
                api_key = api_key,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except ImportError as e:
            print(f'ошибка импорта langchain_openai: {e}')
            return MockLLM()
        except Exception as e:
            print(f'ошибка инициализации deepseek: {e}')
            return MockLLM()

    elif provider == 'mock':
        print('используем mock')
        return MockLLM()
    else:
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