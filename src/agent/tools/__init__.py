# src/agent/tools/__init__.py

# Импортируем все тулзы
from .search import search_in_db, get_salary_stats, get_top_skills
from .parser import parse_resume_text  # раскомментируйте, если создали parser.py

# ✅ Список инструментов для bind_tools
tools = [
    search_in_db,
    get_salary_stats,
    get_top_skills,
    parse_resume_text,
]

__all__ = [
    "tools",
    "search_in_db",
    "get_salary_stats",
    "get_top_skills",
    "parse_resume_text",
]