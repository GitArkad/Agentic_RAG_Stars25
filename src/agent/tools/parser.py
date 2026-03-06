# src/agent/tools/parser.py
import logging
import re
from typing import Dict, Any, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def parse_resume_text(text: str) -> Dict[str, Any]:
    """
    Извлекает структурированные данные из текста резюме.
    """
    logger.info("[PARSER] Обработка текста резюме")
    
    # Простая эвристика для поиска навыков
    skills_keywords = ["python", "java", "docker", "kubernetes", "sql", "git", "linux", 
                       "fastapi", "django", "postgresql", "redis", "aws", "tensorflow"]
    found_skills = [s for s in skills_keywords if s in text.lower()]
    
    # Поиск опыта (число + "лет" или "года")
    exp_match = re.search(r'(\d+)\s*(лет|года|год)', text.lower())
    experience = int(exp_match.group(1)) if exp_match else 0
    
    # Поиск желаемой должности (эвристика)
    role_match = re.search(r'(разработчик|developer|инженер|engineer|аналитик|analyst)', text.lower())
    desired_role = role_match.group(0).title() if role_match else "Специалист"
    
    result = {
        "raw_text": text,
        "desired_role": desired_role,
        "skills": found_skills,
        "experience_years": experience,
        "salary_expectation": 0
    }
    
    logger.info(f"[PARSER] Извлечено навыков: {len(found_skills)}, опыт: {experience}")
    return result

@tool
def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """
    Извлекает текст из файла резюме (PDF, DOCX).
    """
    logger.info(f"[PARSER] Обработка файла: {file_path}")
    # TODO: Реализовать чтение файлов
    return {
        "raw_text": f"[Текст из файла {file_path}]",
        "skills": [],
        "experience_years": 0,
        "desired_role": "",
        "salary_expectation": 0
    }