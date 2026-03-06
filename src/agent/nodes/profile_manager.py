# src/agent/nodes/profile_manager.py
import logging
from typing import Dict, Any
from src.agent.state import State, ResumeData
from src.agent.tools.parser import parse_resume_text

logger = logging.getLogger(__name__)

def profile_manager_node(state: State) -> Dict[str, Any]:
    """
    Node: Context/Profile Manager
    Отвечает за «переваривание» входных данных и фиксацию в State.
    """
    logger.info("[PROFILE_MANAGER] Начало обработки...")
    
    # 1. Получаем последнее сообщение пользователя
    messages = state.get("messages", [])
    if not messages:
        logger.debug("[PROFILE_MANAGER] Нет сообщений, выход")
        return {}
    
    last_message = messages[-1]
    content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # 2. Проверяем, есть ли уже профиль в State (чтобы не парсить повторно)
    if state.get("profile"):
        logger.debug("[PROFILE_MANAGER] Профиль уже загружен, пропускаем")
        return {}
    
    # 3. Определяем, является ли сообщение резюме
    # Эвристика: длинный текст (>200 символов) или ключевые слова
    is_resume = (
        len(content) > 200 or 
        "резюме" in content.lower() or 
        "опыт" in content.lower() or 
        "навыки" in content.lower()
    )
    
    if is_resume:
        logger.info("[PROFILE_MANAGER] Обнаружено резюме, запускаем парсинг...")
        
        try:
            # Вызываем инструмент парсинга
            parsed = parse_resume_text.invoke({"text": content})
            
            # Формируем структурированный профиль
            profile_data: ResumeData = {
                "raw_text": parsed.get("raw_text", ""),
                "desired_role": parsed.get("desired_role", ""),
                "skills": parsed.get("skills", []),
                "experience_years": parsed.get("experience_years", 0),
                "salary_expectation": parsed.get("salary_expectation", 0)
            }
            
            logger.info(f"[PROFILE_MANAGER] Профиль создан: {profile_data.get('desired_role')}")
            
            # ✅ ГЛАВНОЕ: Фиксируем данные в State
            return {
                "profile": profile_data,
                "resume_processed": True
            }
            
        except Exception as e:
            logger.error(f"[PROFILE_MANAGER] Ошибка парсинга: {e}")
            return {}
    
    logger.debug("[PROFILE_MANAGER] Это не резюме, пропускаем")
    return {}