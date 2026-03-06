# src/agent/state.py
from typing import TypedDict, List, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# ==============================================================================
# 1. Структурированные данные из резюме
# ==============================================================================
class ResumeData(TypedDict, total=False):
    """
    Хранит извлеченные данные из резюме кандидата.
    total=False позволяет создавать частичные объекты.
    """
    raw_text: str                # Исходный текст резюме
    desired_role: str            # Желаемая должность
    skills: List[str]            # Список навыков (для поиска)
    experience_years: int        # Опыт работы в годах
    salary_expectation: int      # Ожидаемая зарплата

# ==============================================================================
# 2. Структура вакансии (для списка найденных)
# ==============================================================================
class VacancyFromDB(TypedDict, total=False):
    """
    Единый стандарт вакансии для передачи между нодами и тулзами.
    Соответствует метаданным в Qdrant.
    """
    # Идентификаторы
    id: str                      # id_vac
    url: str                     # url_vac
    
    # Основная информация
    title: str                   # name_vac_new
    company: str                 # employer
    description: str             # description_clean
    
    # Зарплата (Optional, т.к. может отсутствовать)
    salary_min: Optional[int]    # salary_min
    salary_max: Optional[int]    # salary_max
    salary_currency: Optional[str] # salary_val
    
    # Локация и формат
    location: Optional[str]      # region
    
    # Навыки и опыт
    key_skills: List[str]        # key_techno_new (распарсенный список!)
    experience_required: Optional[str]  # work_experience_new
    
    # Для аналитики
    match_score: Optional[float] # Оценка соответствия (0.0 - 1.0)

# ==============================================================================
# 3. ГЛАВНЫЙ STATE (Состояние системы)
# ==============================================================================
class State(TypedDict, total=False):
    """
    Основное состояние графа. Передается в каждую ноду.
    total=False критически важен для сохранения состояния между шагами!
    """
    # 1. История диалога (Автоматически управляется LangGraph)
    messages: Annotated[List[BaseMessage], add_messages]

    # 2. Данные профиля (Сохраняются однажды и используются всегда)
    profile: Optional[ResumeData]

    # 3. Список последних найденных вакансий (Контекст для вопросов)
    # Нода поиска записывает сюда список, Агент читает его для ответов
    last_search_results: List[VacancyFromDB]

    # 4. Флаги и статусы режима работы
    search_mode: bool            # True = режим поиска, False = чат
    resume_processed: bool       # True = резюме уже загружено и обработано
    loop_step: int               # Счетчик шагов (для отладки циклов)