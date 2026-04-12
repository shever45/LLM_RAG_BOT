"""
!!!этот файл не относится к проекту!!!
для меня была непонятна библиотека langgraph, также графы и обход графов(DFS, BFS) это моя любимая тема в алгоритмах,
поэтому я решил сделать небольшое задание,
для того чтобы улучишть свои знания и понимание и уже на основе этого писать агента.
я решил оставить это здесь, для того чтобы показать что я разобрался с базовыми концепциями langgraph
и вы, проверяющий, были лучше ознакомлены с моими навыками
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# описываем форму словаря для передачи данных между узлами
class DemoState(TypedDict):
    message: str    # текущее сообщение
    counter: int    # счетчик шагов
    result: str     # финанльный результат

# создаем первый узел, который будет добвлять '!' в message внутри словаря
def node_add_exclamtion(state: DemoState) -> DemoState:
    print(f'[узел 1] получено: {state["message"]}')
    new_message = state[('message')] + '!'
    print(f'[узел 1] выход: {new_message}')
    # возвращаем  измененные поля, langgraph просто обновит их,
    # не измененные останутся теме же
    return {
        'message': new_message,
        'counter': state["counter"]+1
    }

# 2 узел, такой же механизм, только добавляет '?'
def node_add_question(state: DemoState) -> DemoState:
    print(f'[узел 2] получено: {state["message"]}')
    new_message = state[('message')] + '?'
    print(f'[узел 2] выход: {new_message}')
    return {
        'message': new_message,
        'counter': state["counter"] + 1
    }

#записывает получившуюсю строку в result внутри state
def node_finalize(state: DemoState) -> DemoState:
    print(f'[узел 3] получили: {state["message"]}')
    return {
        "result": f"итог после {state['counter']} шагов: {state['message']}"
    }

# функция решает добавлять вопрос или завершать
def router(state: DemoState) -> Literal["add_quistion", "finalize"]:
    if state['counter'] < 2:
        print(f'[маршрутизатор] Счетчик = {state["counter"]} далее идем в add_question')
        return 'add_question'
    else:
        print(f'[маршрутизатор] Счетчик = {state["counter"]} далее идем в finalize')
        return 'finalize'

# функция собирает весь наш граф
def build_graph():

    # создаем объект графа с нашим типом состояния
    workflow = StateGraph(DemoState)

    # добавляем узлы, которые в будущем будем вызывать
    workflow.add_node('add_exclamtion', node_add_exclamtion)
    workflow.add_node('add_question', node_add_question)
    workflow.add_node('finalize', node_finalize)

    # указываем начальную точку графа
    workflow.set_entry_point('add_exclamtion')

    # указание графу, чтобы после узла exclamtion он переходил в quistion
    workflow.add_edge("add_exclamtion", "add_question")

    # пишем условный переход, который будет соответствовать тому, что нам выдаст router после запуска
    workflow.add_conditional_edges(
        'add_question',
        router,
        {
            'add_question': 'add_question',
            'finalize': 'finalize'
        }
    )

    # объявляем конец графа после узла finalize
    workflow.add_edge('finalize', END)

    return workflow.compile()

if __name__ == '__main__':
    print('демонстрация langgraph')
    graph = build_graph()

    # инициализируем словарь данных для прохода по графу
    initial_state = {
        'message':'Привет',
        'counter': 0,
        'result': ''
    }

    print(f'\nначальное состояние: {initial_state}\n')
    print('-'*30)
    final_state = graph.invoke(initial_state)
    print('-' * 30)
    print(f"\nфинальное состояние: {final_state}")
    print(f"\nрезультат: {final_state['result']}")

