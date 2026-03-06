# src/agent/tools/analysis.py
import logging
from typing import List, Dict, Any, Optional
from collections import Counter
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

def _parse_skills(skills_str: str) -> List[str]:
    """Парсит строку навыков в список"""
    if not skills_str:
        return []
    return [s.strip().lower() for s in skills_str.split(",") if s.strip()]

@tool
def calculate_match_score(resume_skills: List[str], vacancy_skills: str) -> float:
    """
    Рассчитывает процент соответствия навыков резюме требованиям вакансии.
    Returns: Float от 0.0 до 1.0
    """
    if not vacancy_skills:
        return 0.0
    
    vacancy_skills_list = _parse_skills(vacancy_skills)
    resume_skills_lower = [s.lower() for s in resume_skills]
    
    if not vacancy_skills_list:
        return 0.0
    
    matches = set(resume_skills_lower) & set(vacancy_skills_list)
    score = len(matches) / len(vacancy_skills_list)
    
    logger.info(f"[MATCH] Совпадений: {len(matches)}/{len(vacancy_skills_list)} = {score:.2f}")
    return round(score, 2)

@tool
def get_salary_stats(query: str) -> str:
    """
    Анализирует распределение зарплат, игнорируя пустые значения.
    """
    logger.info(f"[ANALYTICS] Аналитика зарплат по запросу: '{query}'")
    
    from src.agent.tools.search import search_vacancies
    docs = search_vacancies.invoke({"query": query, "limit": 15})
    
    if not docs:
        return "Данные для анализа не найдены."
    
    sal_list = []
    for vac in docs:
        s_min = vac.get("salary_min")
        if s_min is not None and str(s_min).lower() != 'nan':
            s_val = vac.get("salary_currency", "RUR")
            sal_list.append(f"{s_min} {s_val}")
    
    if not sal_list:
        return "Во всех найденных вакансиях зарплата не указана."
    
    total = len(sal_list)
    counts = Counter(sal_list)
    
    stats = []
    for sal, count in counts.most_common():
        percentage = (count / total) * 100
        stats.append(f"- {sal}: {percentage:.1f}%")
    
    result = f"📊 Статистика зарплат (min) по запросу '{query}':\n" + "\n".join(stats)
    logger.info(f"[ANALYTICS] Обработано {total} вакансий с ЗП")
    
    return result

@tool
def get_experience_stats(query: str) -> str:
    """
    Анализирует распределение требуемого опыта (в %) для вакансий по запросу.
    """
    logger.info(f"[ANALYTICS] Аналитика опыта по запросу: '{query}'")
    
    from src.agent.tools.search import search_vacancies
    docs = search_vacancies.invoke({"query": query, "limit": 15})
    
    if not docs:
        return "Данные для анализа не найдены."
    
    exp_list = [vac.get("experience_required", "не указано") for vac in docs]
    total = len(exp_list)
    counts = Counter(exp_list)
    
    stats = []
    for exp, count in counts.items():
        percentage = (count / total) * 100
        stats.append(f"- {exp}: {percentage:.1f}%")
    
    result = "📊 Статистика распределения опыта:\n" + "\n".join(stats)
    logger.info(f"[ANALYTICS] Обработано {total} вакансий")
    
    return result

@tool
def get_top_skills(query: str) -> Dict[str, Any]:
    """
    Топ навыков по вакансиям (top-12).
    """
    logger.info(f"[SKILLS] Топ навыков по запросу: '{query}'")
    
    from src.agent.tools.search import search_vacancies
    docs = search_vacancies.invoke({"query": query, "limit": 20})
    
    if not docs:
        return {"query": query, "top_skills": []}
    
    skills_flat = []
    for vac in docs:
        tech = vac.get("key_skills", "")
        if isinstance(tech, str):
            skills_flat.extend([s.strip() for s in tech.split(",") if s.strip()])
    
    top = Counter(skills_flat).most_common(12)
    
    return {
        "query": query,
        "top_skills": [{"skill": skill, "count": count} for skill, count in top]
    }

@tool
def analyze_gaps(resume_skills: List[str], vacancy_skills: str) -> List[str]:
    """
    Находит недостающие навыки (гэпы) между резюме и вакансией.
    """
    vacancy_list = _parse_skills(vacancy_skills)
    resume_lower = [s.lower() for s in resume_skills]
    
    gaps = [skill for skill in vacancy_list if skill not in resume_lower]
    logger.info(f"[GAPS] Найдено {len(gaps)} недостающих навыков")
    
    return gaps