# src/agent/graph.py
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.agent.state import State
from src.agent.nodes.profile_manager import profile_manager_node
from src.agent.nodes.agent import agent_node
from src.agent.tools import tools  # Список тулзов из tools/__init__.py

logger = logging.getLogger(__name__)

# ==============================================================================
# Инициализация ноды для выполнения инструментов
# ==============================================================================
# ToolNode автоматически обрабатывает tool_calls от LLM и возвращает результаты
tool_node = ToolNode(tools)

# ==============================================================================
# Функция маршрутизации: решает, куда идти после агента
# ==============================================================================
def route_agent(state: State) -> Literal["tools", "__end__"]:
    """
    Проверяет последнее сообщение: если есть tool_calls → идём в tools,
    иначе → завершаем выполнение.
    """
    messages = state.get("messages", [])
    if not messages:
        return END
    
    last_message = messages[-1]
    
    # Проверяем, есть ли у сообщения tool_calls (LLM хочет вызвать инструмент)
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        logger.info(f"[ROUTER] Направлено в tools: {[tc['name'] for tc in last_message.tool_calls]}")
        return "tools"
    
    logger.info("[ROUTER] Направлено в END (текстовый ответ)")
    return END

# ==============================================================================
# Создание графа
# ==============================================================================
def create_graph():
    """
    Создаёт и компилирует граф работы агента с поддержкой инструментов.
    
    Flow:
    User Input 
        → Profile Manager 
        → Agent 
        → [если tool_calls → Tools → Agent] 
        → END
    """
    logger.info("[GRAPH] Инициализация графа...")
    
    # 1. Создаём граф с типизированным состоянием
    workflow = StateGraph(State)
    
    # 2. Регистрируем ноды
    workflow.add_node("profile_manager", profile_manager_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)  # ✅ Нода для выполнения инструментов
    
    # 3. Устанавливаем точку входа
    # Сначала всегда идёт Profile Manager (проверяет/обновляет данные)
    workflow.set_entry_point("profile_manager")
    
    # 4. Настраиваем связи между нодами
    
    # Profile Manager → Agent (всегда)
    workflow.add_edge("profile_manager", "agent")
    
    # Agent → [Tools или END] (условный переход)
    workflow.add_conditional_edges(
        "agent",
        route_agent,  # Функция-роутер
        ["tools", END]  # Возможные направления
    )
    
    # Tools → Agent (после выполнения инструмента возвращаемся к агенту для ответа)
    workflow.add_edge("tools", "agent")
    
    # 5. Компилируем граф
    logger.info("[GRAPH] Граф успешно скомпилирован")
    logger.info(f"[GRAPH] Доступные инструменты: {[t.name for t in tools]}")
    
    return workflow.compile()