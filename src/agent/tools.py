# import logging

# from langchain_qdrant import QdrantVectorStore
# from qdrant_client import QdrantClient
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.tools import tool
# from collections import Counter

# logger = logging.getLogger(__name__)

# # Base settings
# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
# client=QdrantClient(path="db/qdrant_db")
# vector_store = QdrantVectorStore(
#     client=client,
#     collection_name="demo_collection",
#     embedding=embeddings
#     )

# @tool
# def search_in_db(query: str):
#     """
#     поиск вакансий в БД Москвы
#     """

#     docs = vector_store.similarity_search(query, k=3)
#     return "\n\n".join([f"Вакансия: {d.page_content}\nМета: {d.metadata}" for d in docs])

# # Блок аналитикиЖ закрыть
# # def get_expirience_stats(query: str):
# #     """
# #     Анализирует распределение требуемого опыта (в %) для вакансий по запросу
# #     """

# #     print(f"\n[ВЫЗОВ ИНСТРУМЕНТА]: Аналитика опыта по запросу '{query}'...")
# #     logger.info(f"Начало сбора статистики для: {query}")

# #     docs = vector_store.similarity_search(query, k=3)

# #     if not docs:
# #         print("[ОШИБКА]: Данные не найдены!")
# #         return "Данные для анализа не найдены."
    
# #     exp_list = [d.metadata.get("work_experience_new", "не указано") for d in docs]
# #     total = len(exp_list)
# #     counts = Counter(exp_list)

# #     print(f"[ИНФО]: Обработано {total} вакансий. Считаем проценты...")

# #     stats = []

# #     for exp, count in counts.items():
# #         percentage = (count/total) * 100
# #         stats.append(f"- {exp} лет: {percentage:.1f}%")

# #     result = "Cтатистика распределения опыта в Москве:\n" + "\n".join(stats)

# #     print("[УСПЕХ]: Аналитика сформирована и передана агенту.")
# #     return result

# # Блок аналитики зарплаты
# @tool
# def get_salary_stats(query: str):
#     """
#     Анализирует распределение зарплат, игнорируя пустые значения (NaN)
#     """
#     print(f"\n[ВЫЗОВ ИНСТРУМЕНТА]: Аналитика зарплат по запросу '{query}'...")
    
#     # Берем чуть больше вакансий для точности, но следим за лимитами (k=15)
#     docs = vector_store.similarity_search(query, k=15)

#     if not docs:
#         return "Данные для анализа не найдены."
    
#     sal_list = []
#     for d in docs:
#         m = d.metadata
#         s_min = m.get("salary_min")
        
#         # Фильтр: проверяем, что значение есть, оно не None и не строка 'nan'
#         if s_min is not None and str(s_min).lower() != 'nan':
#             # Достаем валюту, если её нет — ставим RUR по умолчанию
#             s_val = m.get("salary_val", "RUR")
#             # Приводим к красивому виду: "150000.0 RUR"
#             sal_list.append(f"{s_min} {s_val}")

#     if not sal_list:
#         return "Во всех найденных вакансиях зарплата не указана."

#     total = len(sal_list)
#     counts = Counter(sal_list)

#     print(f"[ИНФО]: Успешно обработано {total} вакансий с указанной ЗП.")

#     stats = []
#     # Сортируем для порядка (по убыванию количества)
#     for sal, count in counts.most_common():
#         percentage = (count / total) * 100
#         stats.append(f"- {sal}: {percentage:.1f}%")

#     result = f"Статистика зарплат (min) в Москве по запросу '{query}':\n" + "\n".join(stats)
    
#     print("[УСПЕХ]: Аналитика очищена от пустых значений и передана агенту.")
#     return result


# # Список tools 

# # Список tools 
# tools = [
#     search_in_db,
#     get_salary_stats
#     # get_expirience_stats
# ]

# @tool
# def get_top_skills(query: str):
#     """
#     Топ навыков по вакансиям (берем top-20 по смыслу и считаем частоты).
#     """
#     logger.info(f"Топ навыков: {query}")

#     docs = vector_store.similarity_search(query, k=20)

#     if not docs:
#         return {"query": query, "top_skills": []}

#     skills_flat: list[str] = []

#     for d in docs:
#         md = d.metadata or {}
#         tech = md.get("key_techno_new") or md.get("skills")

#         if isinstance(tech, str):
#             skills_flat.extend([s.strip() for s in tech.split(",") if s.strip()])
#         elif isinstance(tech, list):
#             skills_flat.extend([str(s).strip() for s in tech if str(s).strip()])

#     top = Counter(skills_flat).most_common(12)

#     return {
#         "query": query,
#         "top_skills": [{"skill": skill, "count": count} for skill, count in top]
#     }