from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END

# импортируем функции
# load_docs - все содержимое из data в dict
# search - поиск в текстов по ключевым словам
# get_llm - инициализации llm, если нет доступа к llm используется заготовленные ответы по контексту
from app.rag import load_docs, search
from app.llm import get_llm

# инициализируем словарь данных для прохода по графу
class AgentState(TypedDict):
    # история переписки типа: [{role: user, content: привет}]
    messages: list[Dict[str,str]]
    #последнее сообщение пользователя state[messages][-1][content]
    current_query: str
    # здесь находится содержимое найденного файла
    retrieved_context:str
    # нужно ли уточнение, если 'стипендия' in message, но не сказано про страну
    needs_clarification: bool
    # текст уточнения
    clarification_question: str
    # обратный ответ llm
    final_response: str


# сразу подгружаем всю документацию
documents = load_docs()
print(f'загружено docs: {len(documents)}')


# ищем контекст для последнего сообщения и обновляем его в state
def retrieve_node(state: AgentState) -> Dict[str,Any]:
    query = state['current_query']
    print(f'ищу контекст для: "{query}"')
    context = search(query, documents)
    context_len = len(context) if context else 0
    print(f'найден контекст длиной: {context_len}')

    return {
        "retrieved_context": context or ""
    }

# проверка на то, нужно ли уточнение города (франция или германия)
# проверяем находятся упоминание страны в query и context
# а также слова которые на пряму не указывают на страну(country_sensetive_keywords)
def check_clarification_node(state: AgentState) -> Dict[str, Any]:
    query = state['current_query'].lower()
    context = state['retrieved_context']
    if context is None:
        context = ""
    context = context.lower()
    country_sensetive_keywords = ["стипендия", "налог", "виза", "рабочий день", "ставка", "зарплата", "деньги", "сколько платят"]

    countries = ['германия', 'франция', 'берлин', 'париж']

    has_sensetive = any(kw in query for kw in country_sensetive_keywords)

    country_mentioned = any(c in query or c in context for c in countries)

    needs_clarification = False
    clarification_question = ''

    if has_sensetive and not country_mentioned:
        needs_clarification = True
        if 'стипендия' in query or 'сколько платят' in query:
            topic = 'размере стипендии'
        elif 'налог' in query:
            topic = 'налогах'
        elif 'виза' in query:
            topic = 'визовых требованиях'
        else:
            topic = 'условиях стажировки'

        clarification_question = f'Для точного ответа о {topic} пожалуйста уточните страну: Германия или Франция'

        print(f'уточните страну. Тема о {topic}')
    else:
        print(f'уточнение не требуется.')
    return {
        'needs_clarification': needs_clarification,
        'clarification_question': clarification_question
    }

# создает ответ, и обновляет его в state
def ask_clarification(state: AgentState) -> Dict[str, Any]:
    question = state['clarification_question']
    print(f'Ответ: "{question}"')

    return {
        "final_response":question
    }



def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    query = state['current_query']
    context = state['retrieved_context']
    history = state['messages']

    print(f'Генерируется ответ через LLM...')

    # инициализируем какой llm будем пользоваться
    llm = get_llm()
    system_prompt = """Ты — официальный консультант программы международной стажировки "CdekStart".
    СТРОГИЕ ПРАВИЛА (СОБЛЮДАЙ ИХ ОБЯЗАТЕЛЬНО):
    1. Отвечай только на основе информации, предоставленной в контексте ниже.
    2. Если в контексте нет ответа на вопрос, честно скажи: "В моей базе знаний нет такой информации."
    3. НЕ придумывай факты, цифры, даты или правила.
    4. НЕ используй знания о стажировках из других источников.
    5. Если вопрос не относится к стажировке, вежливо напомни, что ты консультируешь только по программе CdekStart.
    6. Отвечай на русском языке, вежливо и профессионально.
    7. Если информация в контексте противоречива, укажи на это и предложи уточнить.
    
    ФОРМАТ ОТВЕТА:
    - Сначала прямой ответ на вопрос.
    - При необходимости, краткое пояснение из контекста."""

    # сохраняем историю 3 последних сообщения пользователя и 3 llm
    history_text = ''
    for msg in history[-6:]:
        role = 'Пользователь' if msg['role']=='user' else 'Ассистент'
        history_text+=f'{role}:{msg["content"]}\n'

    user_prompt = f"""КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ (ИСПОЛЬЗУЙ ТОЛЬКО ЭТУ ИНФОРМАЦИЮ):
    --- НАЧАЛО КОНТЕКСТА ---
    {context}
    --- КОНЕЦ КОНТЕКСТА ---
    
    ИСТОРИЯ ДИАЛОГА:
    {history_text if history_text else "(Это первое сообщение)"}
    
    ТЕКУЩИЙ ВОПРОС ПОЛЬЗОВАТЕЛЯ: {query}
    
    ТВОЙ ОТВЕТ (СТРОГО НА ОСНОВЕ КОНТЕКСТА):"""

    messages_for_llm = [
        {'role':'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    try:
        response = llm.invoke(messages_for_llm)
        if hasattr(response, 'content'):
            answer = response.content
        elif isinstance(response, str):
            answer = response
        else:
            answer = str(response)
        print(f'LLM ответила: {len(answer)} символов')
    except Exception as e:
        print(f"[ошибка llm: {e}")
        answer = f"произошла ошибка при обращении к llm. Пожалуйста, попробуйте позже. (Ошибка: {e})"

    return {
        'final_response': answer
    }

#происходит перенаправление графа на другую функцию,
# при надобности в уточнении запроса
def router_clarification(state: AgentState) -> Literal['ask_clarification', 'generate_answer']:
    if state["needs_clarification"]:
        return 'ask_clarification'
    else:
        return 'generate_answer'

# строим граф полностью
def build_graph():
    # создаем объект графа с нашим типом состояния
    workflow = StateGraph(AgentState)

    # добавляем узлы, которые в будущем будем вызывать
    workflow.add_node('retrieve', retrieve_node)
    workflow.add_node('check_clarification', check_clarification_node)
    workflow.add_node('ask_clarification', ask_clarification)
    workflow.add_node('generate_answer', generate_answer_node)

    # указываем начальную точку графа
    workflow.set_entry_point('retrieve')

    # указание графу, чтобы после узла retrieve он переходил в check_clarification
    workflow.add_edge("retrieve", "check_clarification")

    # пишем условный переход, который будет соответствовать тому, что нам выдаст router после запуска
    workflow.add_conditional_edges(
        'check_clarification',
        router_clarification,
        {
            "ask_clarification": "ask_clarification",
            "generate_answer": "generate_answer"
        }
    )

    # объявляем концы графа
    workflow.add_edge("ask_clarification", END)
    workflow.add_edge("generate_answer", END)

    compiled_graph = workflow.compile()
    print('graph compiled')
    return compiled_graph

agent_graph = build_graph()
def chat_with_agent(user_message: str, history: List[Dict[str,str]] = None) -> Dict[str, Any]:
    if history is None:
        history = []

    initial_state: AgentState = {
        'messages': history.copy(),
        'current_query': user_message,
        'retrieved_context': '',
        'needs_clarification': False,
        'clarification_question': '',
        'final_response':'',
    }

    final_state = agent_graph.invoke(initial_state)

    response = final_state['final_response']

    updated_history = history.copy()
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": response})

    return {
        "response": response,
        "history": updated_history,
        "needs_clarification": final_state["needs_clarification"]
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ АГЕНТА")
    print("=" * 60)

    history = []

    # тест 1: общий вопрос
    print("\n--- тест 1: общий вопрос ---")
    result = chat_with_agent("Как попасть на стажировку?", history)
    history = result["history"]
    print(f"Бот: {result['response']}")

    # тест 2: вопрос про стипендию (должен запросить уточнение)
    print("\n--- тест 2: вопрос про стипендию ---")
    result = chat_with_agent("Какая стипендия?", history)
    history = result["history"]
    print(f"Бот: {result['response']}")
    print(f"Требуется уточнение: {result['needs_clarification']}")

    # тест 3: уточнение страны
    print("\n--- тест 3: цточнение страны ---")
    result = chat_with_agent("Германия", history)
    history = result["history"]
    print(f"Бот: {result['response']}")

