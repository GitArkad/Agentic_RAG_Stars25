# src/agent/tools/search.py
import logging
from typing import List, Dict, Any
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from collections import Counter

logger = logging.getLogger(__name__)

# ==============================================================================
# Инициализация (выносится на уровень модуля)
# ==============================================================================
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
client = QdrantClient(path="db/qdrant_db")
vector_store = QdrantVectorStore(
    client=client,
    collection_name="demo_collection",
    embedding=embeddings
)

# ==============================================================================
# Тулз: Поиск вакансий
# ==============================================================================
@tool
def search_in_db(query: str) -> str:
    """
    Поиск вакансий в БД по запросу.
    Возвращает отформатированную строку с результатами.
    
    Args:
        query: Поисковый запрос (навыки, должность, локация)
    
    Returns:
        Строка с описанием найденных вакансий
    """
    logger.info(f"[SEARCH] Поиск по запросу: '{query}'")
    
    docs = vector_store.similarity_search(query, k=5)
    
    if not docs:
        logger.warning("[SEARCH] Вакансии не найдены")
        return "По вашему запросу вакансии не найдены."
    
    results = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata or {}
        results.append(
            f"Вакансия #{i}:\n"
            f"  Title: {meta.get('name_vac_new', 'N/A')}\n"
            f"  Company: {meta.get('employer', 'N/A')}\n"
            f"  Location: {meta.get('region', 'N/A')}\n"
            f"  Skills: {meta.get('key_techno_new', 'N/A')}\n"
            f"  Salary: {meta.get('salary_min', 'N/A')} - {meta.get('salary_max', 'N/A')} {meta.get('salary_val', '')}\n"
            f"  Description: {doc.page_content[:200]}..."
        )
    
    logger.info(f"[SEARCH] Найдено {len(results)} вакансий")
    return "\n\n".join(results)

# ==============================================================================
# Тулз: Статистика зарплат
# ==============================================================================
@tool
def get_salary_stats(query: str) -> str:
    """
    Анализирует распределение зарплат по вакансиям.
    Игнорирует пустые значения (NaN).
    
    Args:
        query: Поисковый запрос для фильтрации вакансий
    
    Returns:
        Строка со статистикой зарплат в процентах
    """
    logger.info(f"[ANALYTICS] Статистика зарплат по запросу: '{query}'")
    
    docs = vector_store.similarity_search(query, k=15)
    
    if not docs:
        return "Данные для анализа не найдены."
    
    sal_list = []
    for doc in docs:
        meta = doc.metadata or {}
        s_min = meta.get("salary_min")
        
        # Фильтр: пропускаем пустые/невалидные значения
        if s_min is not None and str(s_min).lower() not in ("", "nan", "none"):
            currency = meta.get("salary_val", "RUR")
            sal_list.append(f"{s_min} {currency}")
    
    if not sal_list:
        return "Во всех найденных вакансиях зарплата не указана."
    
    # Считаем проценты
    total = len(sal_list)
    counts = Counter(sal_list)
    
    stats = []
    for sal, count in counts.most_common():
        percentage = (count / total) * 100
        stats.append(f"- {sal}: {percentage:.1f}%")
    
    result = f"📊 Статистика зарплат (min) по запросу '{query}':\n" + "\n".join(stats)
    logger.info(f"[ANALYTICS] Обработано {total} вакансий с ЗП")
    
    return result

# ==============================================================================
# Тулз: Топ навыков
# ==============================================================================
@tool
def get_top_skills(query: str) -> Dict[str, Any]:
    """
    Возвращает топ-12 наиболее частых навыков в вакансиях.
    
    Args:
        query: Поисковый запрос для фильтрации вакансий
    
    Returns:
        Словарь: {"query": ..., "top_skills": [{"skill": ..., "count": ...}, ...]}
    """
    logger.info(f"[SKILLS] Топ навыков по запросу: '{query}'")
    
    docs = vector_store.similarity_search(query, k=20)
    
    if not docs:
        return {"query": query, "top_skills": []}
    
    # Собираем все навыки в один список
    skills_flat = []
    for doc in docs:
        meta = doc.metadata or {}
        tech = meta.get("key_techno_new", "")
        
        if isinstance(tech, str):
            # Парсим строку "Python, Docker, FastAPI" → ["python", "docker", "fastapi"]
            skills_flat.extend([s.strip().lower() for s in tech.split(",") if s.strip()])
    
    # Считаем частоту и берем топ-12
    top = Counter(skills_flat).most_common(12)
    
    result = {
        "query": query,
        "top_skills": [{"skill": skill, "count": count} for skill, count in top]
    }
    
    logger.info(f"[SKILLS] Найдено {len(skills_flat)} навыков, топ-12 возвращено")
    return result