# src/agent/nodes/agent.py
import logging
import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from langchain_core.messages import AIMessage, ToolMessage
load_dotenv()
from langchain_groq import ChatGroq
from src.agent.state import State
from src.agent.tools import tools  # Импортируем список тулзов

logger = logging.getLogger(__name__)

# ==============================================================================
# Инициализация LLM с привязанными инструментами
# ==============================================================================
llm = ChatGroq(
    model='openai/gpt-oss-120b',  # ✅ Проверьте название модели в Groq Console
    temperature=0,
    groq_api_key=os.getenv('GROQ_API_KEY')
)
llm_with_tools = llm.bind_tools(tools)

# ==============================================================================
# Нода агента
# ==============================================================================
def agent_node(state: State) -> Dict[str, Any]:
    """
    Node: Agent
    Основной «мозг». Принимает решения о вызове инструментов через LLM.
    """
    logger.info("[AGENT] Начало обработки...")
    
    # 1. Получаем контекст из State
    profile = state.get("profile")
    vacancies = state.get("last_search_results", [])
    
    # 2. Получаем историю сообщений
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="Я готов к работе. Загрузите резюме или спросите о вакансиях.")]}
    
    # 3. Формируем системный промпт с контекстом
    system_prompt = _build_system_prompt(profile, vacancies)
    
    # Добавляем системное сообщение в начало, если его нет
    if not any(isinstance(m, dict) and m.get("role") == "system" for m in messages):
        messages = [{"role": "system", "content": system_prompt}] + messages
    
    # 4. Вызываем LLM с привязанными инструментами
    logger.info(f"[AGENT] Вызов LLM с {len(tools)} инструментами")
    response = llm_with_tools.invoke(messages)
    
    # 5. Обрабатываем ответ
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # LLM хочет вызвать инструмент — возвращаем tool_calls для выполнения
        logger.info(f"[AGENT] Tool calls: {[tc['name'] for tc in response.tool_calls]}")
        return {"messages": [response]}
    
    # 6. Обычный текстовый ответ
    logger.info("[AGENT] Текстовый ответ")
    return {"messages": [response]}

# ==============================================================================
# Вспомогательная функция: системный промпт с контекстом
# ==============================================================================
def _build_system_prompt(profile: dict, vacancies: List[dict]) -> str:
    """Формирует системный промпт с учётом профиля и найденных вакансий"""
    
    parts = [
        "Ты — AI Career Partner, интеллектуальный рекрутинг-ассистент.",
        "Твоя задача: помогать кандидатам с поиском работы, анализом резюме и вакансий.",
        "Отвечай на русском языке, будь дружелюбным и профессиональным.",
        "",
        "Доступные инструменты:",
        "• search_in_db(query) — поиск вакансий в базе по запросу",
        "• get_salary_stats(query) — статистика зарплат",
        "• get_top_skills(query) — топ востребованных навыков",
    ]
    
    # Добавляем контекст профиля, если есть
    if profile:
        parts.extend([
            "",
            "📋 КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:",
            f"• Должность: {profile.get('desired_role', 'Не указана')}",
            f"• Опыт: {profile.get('experience_years', 0)} лет",
            f"• Навыки: {', '.join(profile.get('skills', [])[:5])}",
            f"• Ожидаемая ЗП: {profile.get('salary_expectation', 'Не указана')} руб.",
        ])
    
    # Добавляем контекст вакансий, если есть
    if vacancies:
        parts.extend([
            "",
            "🔍 ПОСЛЕДНИЙ ПОИСК ВАКАНСИЙ:",
            f"Найдено {len(vacancies)} вакансий. Пользователь может спрашивать:",
            "• 'Какая зарплата в лучшей?'",
            "• 'В какой компании стек ближе к моему?'",
            "• 'Покажи детали вакансии'",
            "",
            "Краткая информация о вакансиях:",
        ])
        for i, vac in enumerate(vacancies[:3], 1):  # Показываем топ-3
            parts.append(
                f"{i}. {vac.get('title', 'N/A')} в {vac.get('company', 'N/A')} | "
                f"Match: {vac.get('match_score', 0)*100:.0f}%"
            )
    
    return "\n".join(parts)